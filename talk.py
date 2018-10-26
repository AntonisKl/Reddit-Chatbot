import calendar

import reddit
import time

if __name__ == '__main__':

    ####### PARAMETERS ######
    maxReplyLength = 20
    submissionTitleKeywords = ["I "]
    submissionTextKeywords = [" am "]
    commentKeywords = [""]
    submissionMinScore = 4
    commentMinScore = 5
    subredditNameRepost = "aliens"
    subredditNameReply = "cars"
    replySubmissionDaysAgoFrom = 200  # from 20 days ago
    replySubmissionDaysAgoTo = 0  # ...to today (0 days from today and backwards)
    sleepTimeInMinutesForSubmissions = 15
    sleepTimeInMinutesForReplies = 10
    sleepTimeInMinutesForCommentDeletion = 1
    maxReplyLengthEnabled = True
    submissionPostEnabled = True
    replyPostEnabled = True
    specifiedSubmissionSearch = True
    replySpecified = True
    deleteNegativeComments = True
    ####### END OF PARAMETERS ######

    now = 0
    prevTimeSub = 0
    prevTimeReply = 0
    prevTimeDeletion = 0
    unixSleepTimeSub = sleepTimeInMinutesForSubmissions * 60
    unixSleepTimeReply = sleepTimeInMinutesForReplies * 60
    unixSleepTimeDeletion = sleepTimeInMinutesForCommentDeletion * 60
    while True:
        if submissionPostEnabled:
            now = calendar.timegm(time.gmtime())
            if (now - prevTimeSub) >= unixSleepTimeSub:
                print(now - prevTimeSub)
                if specifiedSubmissionSearch:
                    reddit.submissionSpecifiedSearch(subredditNameRepost, submissionTitleKeywords, submissionTextKeywords, 4)
                else:
                    reddit.random_submission()
                prevTimeSub = now

        if replyPostEnabled:
            now = calendar.timegm(time.gmtime())
            if (now - prevTimeReply) >= unixSleepTimeReply:
                print(now - prevTimeReply)
                if replySpecified:
                    if maxReplyLengthEnabled:
                        reddit.replySpecified(replySubmissionDaysAgoFrom * 86400, replySubmissionDaysAgoTo * 86400, subredditNameReply, submissionTitleKeywords, submissionTextKeywords, commentKeywords, minSubmissionScore=submissionMinScore, minCommentScore=commentMinScore, maxReplyLength=maxReplyLength)
                    else:
                        reddit.replySpecified(replySubmissionDaysAgoFrom * 86400, replySubmissionDaysAgoTo * 86400, subredditNameReply, submissionTitleKeywords, submissionTextKeywords, commentKeywords, minSubmissionScore=submissionMinScore, minCommentScore=commentMinScore)
                else:
                    reddit.random_reply()
                prevTimeReply = now

        if deleteNegativeComments:
            now = calendar.timegm(time.gmtime())
            if (now - prevTimeDeletion) >= unixSleepTimeDeletion:
                reddit.deleteNegativeComments()
                prevTimeDeletion = now
