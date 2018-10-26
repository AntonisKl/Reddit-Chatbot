import calendar

import praw
import time
import bot
import settings

import urllib2
import json
import random

api = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                  client_secret=settings.REDDIT_SECRET,
                  password=settings.REDDIT_PASSWORD,
                  user_agent=settings.REDDIT_USER_AGENT,
                  username=settings.REDDIT_USERNAME)


def submission_timespan(daysNum):
    # Get the current epoch time, and then subtract one year
    year_ago = int(time.time()) - 31622400 - (daysNum * 86400)
    # Add 2 weeks to the time from a year ago
    end_search = year_ago + (daysNum * 86400)
    # Return a tuple with the start/end times to search old submissions
    return (year_ago, end_search)


def random_submission():
    # Get submissions from a random subreddit one year ago

    submissions = urllib2.urlopen("https://api.pushshift.io/reddit/submission/search/?after={}&before={}".format(submission_timespan()[0], submission_timespan()[1])).read()
    if submissions:
        # print(json.loads(submissions))
        submissionsJson = json.loads(submissions)["data"]
        print(submissionsJson)
        selectedJson = random.choice(submissionsJson)
        selected = api.submission(selectedJson["id"])
        # selected = api.subreddit("random").random()   # this is for totally random submission
        # print("Submission chosen: " + str(selected))

        # print "Got submission"

        try:
            # Check if the we're reposting a selfpost or a link post.
            # Set the required params accodingly, and reuse the content
            # from the old post
            if selected.is_self:
                params = {"title": selected.title, "selftext": selected.selftext}
            else:
                params = {"title": selected.title, "url": selected.url}

            # Submit the same content to the same subreddit. Prepare your salt picks
            api.subreddit(selected.subreddit.display_name).submit(**params)
        except Exception as e:
            print e


def submissionSpecifiedSearch(subredditName, titleKeywords, textKeywords, minScore):
    sort_types = ["score", "num_comments", "created_utc"]
    sort_order = ["asc", "desc"]
    boolean_values = ["true", "false"]
    operators = ["=>", "=<"]

    curUserSubmissions = list(api.user.me().submissions.new(limit=10))

    print "Searching for a submission to post, please wait..."
    timespan = submission_timespan(random.randint(0, 175))
    submissionPosted = False
    url = "https://api.pushshift.io/reddit/submission/search/?subreddit=" + str(subredditName) + "&is_self=" + random.choice(boolean_values) + \
          "&is_video=" + random.choice(boolean_values) + "&score=>" + str(minScore) + "&size=500&after=" + str(timespan[0]) + \
          "&before=" + str(timespan[1]) + "&sort_type=" + random.choice(sort_types) + "&sort=" + random.choice(sort_order) + "&filter=id"

    # print (url)

    submissions = None

    error = True
    while error:
        try:
            submissions = urllib2.urlopen(url).read()
            error = False
        except urllib2.HTTPError as e:
            print 'There was an error with the request, code: ' + str(e.code) + ". Retrying..."

    submissionsJson = json.loads(submissions)["data"]

    tries = 0

    while not submissionPosted:

        # print(submissions)

        if "id" in submissions and tries <= 10:

            if tries < len(submissionsJson):
                selectedJson = submissionsJson[tries]
                tries += 1
            else:
                selectedJson = random.choice(submissionsJson)
                tries = 11

            # print(len(submissionsJson))

            selected = api.submission(selectedJson["id"])
            submissionAlreadyPosted = False
            # print("hello " + str(list(curUserSubmissions)))
            for submission in curUserSubmissions:
                # print "my submission's title: " + str(submission.title) + "         selected submission's title: " + str(selected.title)
                if submission.title == selected.title:
                    submissionAlreadyPosted = True
                    break

            # print("Submission chosen: " + selectedJson["id"])

            # print "Got a submission"

            if not submissionAlreadyPosted:
                # Check if the we're reposting a selfpost or a link post.
                # Set the required params accodingly, and reuse the content
                # from the old post

                # print(selected.id)
                if selected.is_self:
                    params = {"title": selected.title, "selftext": selected.selftext}
                    # print "Submission score: " + str(selected.score)
                    if any(keyword in params["selftext"].encode('utf-8') for keyword in textKeywords):
                        # else:
                        #     params = {"title": selected.title, "url": selected.url}
                        try:
                            # Submit the same content to the same subreddit. Prepare your salt picks
                            api.subreddit(selected.subreddit.display_name).submit(**params)
                            print "Submission posted..."
                            submissionPosted = True
                        except Exception as e:
                            print e
                            break
                else:
                    params = {"title": selected.title, "url": selected.url}
                    # print "Submission score: " + str(selected.score)
                    if any(keyword in params["title"].encode('utf-8') for keyword in titleKeywords):
                        # else:
                        #     params = {"title": selected.title, "url": selected.url}
                        try:
                            # Submit the same content to the same subreddit. Prepare your salt picks
                            api.subreddit(selected.subreddit.display_name).submit(**params)
                            print "Submission posted..."
                            submissionPosted = True
                        except Exception as e:
                            print e
                            break
        else:
            tries = 0
            timespan = submission_timespan(random.randint(0, 175))
            url = "https://api.pushshift.io/reddit/submission/search/?subreddit=" + str(subredditName) + "&is_self=" + random.choice(boolean_values) + \
                  "&is_video=" + random.choice(boolean_values) + "&score=>" + str(minScore) + "&size=500&after=" + str(timespan[0]) + \
                  "&before=" + str(timespan[1]) + "&sort_type=" + random.choice(sort_types) + "&sort=" + random.choice(sort_order) + "&filter=id"

            # print (url)

            submissions = None

            error = True
            while error:
                try:
                    submissions = urllib2.urlopen(url).read()
                    error = False
                except urllib2.HTTPError as e:
                    print 'There was an error with the request, code: ' + str(e.code) + ". Retrying..."

            submissionsJson = json.loads(submissions)["data"]


def random_reply():
    # Choose a random submission from /r/all that is currently hot
    submission = random.choice(list(api.subreddit('all').hot()))
    # Replace the "MoreReplies" with all of the submission replies
    submission.comments.replace_more(limit=0)

    # Choose a random top level comment
    comment = random.choice(submission.comments.list())

    try:
        # Pass the users comment to chatbrain asking for a reply
        response = bot.brain.reply(comment.body)
    except Exception as e:
        print e

    try:
        # Reply tp the same users comment with chatbrains reply
        comment.reply(response)
    except Exception as e:
        print "reply FAILED"


def replySpecified(daysAgoFrom, daysAgoTo, subredditName, submissionTitleKeywords, submissionTextKeywords, commentKeywords, minSubmissionScore, minCommentScore, maxReplyLength=None):
    sort_types = ["score", "num_comments", "created_utc"]
    sort_order = ["asc", "desc"]
    boolean_values = ["true", "false"]
    operators = ["=>", "=<"]
    signs = [-1, 1]

    curUserComments = list(api.user.me().comments.new(limit=10))
    curUserCommentedSubmissions = []
    for comment in list(curUserComments):
        curUserCommentedSubmissions.append(comment.parent().parent())

    posted = False
    print "Searching for a submission to reply to a comment, please wait..."

    unixNow = calendar.timegm(time.gmtime())
    unixFrom = unixNow - daysAgoFrom + random.randint(0, 100)
    unixTo = unixNow - daysAgoTo - random.randint(0, 100)

    url = "https://api.pushshift.io/reddit/submission/search/?subreddit=" + str(subredditName) + "&is_self=" + random.choice(boolean_values) + \
          "&is_video=" + random.choice(boolean_values) + "&score=>" + str(minSubmissionScore) + "&size=500&after=" + str(unixFrom) + \
          "&before=" + str(unixTo) + "&sort_type=" + random.choice(sort_types) + "&sort=" + random.choice(sort_order) + "&filter=id"

    # print (url)

    submissions = None

    error = True
    while error:
        try:
            submissions = urllib2.urlopen(url).read()
            error = False
        except urllib2.HTTPError as e:
            print 'There was an error with the request, code: ' + str(e.code) + ". Retrying..."

    tries = 0
    while not posted:
        if "id" in submissions and tries <= 10:
            submissionsJson = json.loads(submissions)["data"]

            if tries < len(submissionsJson):
                selectedJson = submissionsJson[tries]
                tries += 1
            else:
                selectedJson = random.choice(submissionsJson)
                tries = 11

            selected = api.submission(selectedJson["id"])

            # print(selected.id)

            submissionAlreadyCommented = False
            for submission in curUserCommentedSubmissions:
                # print str(comment.parent().parent().title)
                if submission.title == selected.title:
                    submissionAlreadyCommented = True
                    break

            if not submissionAlreadyCommented:
                if selected.is_self:
                    params = {"title": selected.title, "selftext": selected.selftext}
                    # print "Got a submission"
                    if any(keyword in params["selftext"].encode('utf-8') for keyword in submissionTextKeywords):
                        if postReply(selected, minCommentScore, commentKeywords, maxReplyLength):
                            posted = True
                else:
                    params = {"title": selected.title, "url": selected.url}
                    # print "Got a submission"
                    if any(keyword in params["title"].encode('utf-8') for keyword in submissionTitleKeywords):
                        if postReply(selected, minCommentScore, commentKeywords, maxReplyLength):
                            posted = True
        else:
            tries = 0
            unixNow = calendar.timegm(time.gmtime())
            unixFrom = unixNow - daysAgoFrom + random.randint(0, 100)
            unixTo = unixNow - daysAgoTo - random.randint(0, 100)

            url = "https://api.pushshift.io/reddit/submission/search/?subreddit=" + str(subredditName) + "&is_self=" + random.choice(boolean_values) + \
                  "&is_video=" + random.choice(boolean_values) + "&score=>" + str(minSubmissionScore) + "&size=500&after=" + str(unixFrom) + \
                  "&before=" + str(unixTo) + "&sort_type=" + random.choice(sort_types) + "&sort=" + random.choice(sort_order) + "&filter=id"

            # print (url)

            submissions = None

            error = True
            while error:
                try:
                    submissions = urllib2.urlopen(url).read()
                    error = False
                except urllib2.HTTPError as e:
                    print 'There was an error with the request, code: ' + str(e.code) + ". Retrying..."
        # else:
        #     print "No submissions found with the selected parameters. Please try providing looser ones."


def postReply(selectedSubmission, minCommentScore, commentKeywords, maxReplyLength):
    selectedSubmission.comment_sort = "best"
    # Replace the "MoreReplies" with all of the submission replies
    selectedSubmission.comments.replace_more(limit=0)

    if selectedSubmission.comments.list():
        bestComment = selectedSubmission.comments.list()[0]
        # print "comment score: " + str(bestComment.score)
        if bestComment.score >= minCommentScore:
            if any(keyword in bestComment.body.encode('utf-8') for keyword in commentKeywords):
                try:
                    # Pass the users comment to chatbrain asking for a reply
                    response = bot.brain.reply(bestComment.body, 5000, maxReplyLength)
                except Exception as e:
                    print e

                tries = 0
                replyFailed = True
                while replyFailed and tries < 5:
                    tries += 1
                    try:
                        # Reply tp the same users comment with chatbrains reply
                        bestComment.reply(response)
                        replyFailed = False
                        print "Reply posted"
                    except Exception as e:
                        print "reply FAILED"
                return True
    return False


def deleteNegativeComments():
    myComments = api.user.me().comments.new()

    counter = 0
    for comment in myComments:
        # print comment.score
        if comment.score < -4:
            comment.delete()
            counter += 1

    print "Deleted " + str(counter) + " comments"
