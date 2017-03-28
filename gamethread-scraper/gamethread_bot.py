import datetime
import praw

# Check for pattern in title
def pattern_in_title(m_title, m_list):
    for pattern in m_list:
        if pattern in m_title:
            return True
    return False

# Check if link has already been submitted
def already_submitted(link, link_list):
    for url in link_list:
        if url == link:
            return True
    return False


USER_AGENT = "Gamethread Scraper v0.1 by /u/vishnumad"
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
REFRESH_TOKEN = ''

try:

    # Initialize reddit client using OAuth2
    r = praw.Reddit(user_agent=USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    # PRINTS OUT REFRESH TOKEN DURING INITIAL RUN
    # url = r.get_authorize_url('uniqueKey', 'identity read submit', True)
    # import webbrowser
    # webbrowser.open(url)
    # code = raw_input("input code: ")
    # access_information = r.get_access_information(code)
    # r.set_access_credentials(**access_information)
    # print access_information["refresh_token"]

    r.refresh_access_information(REFRESH_TOKEN)

    # Get posts from /r/RedditGameThreads and add links to list
    print "Fetching posts from /r/RedditGameThreads"
    main_subreddit = r.get_subreddit("RedditGameThreads", fetch=True)
    main_list = main_subreddit.get_new(limit=25)
    url_list = []
    for post in main_list:
        url_list.append(post.url)

    # Get current time in seconds UTC
    now = datetime.datetime.utcnow()
    now_s = int((now - datetime.datetime(1970, 1, 1)).total_seconds())

    # Match and discard lists
    match_list = ["Match Thread",
                  "Race Thread",
                  "Race Discussion",
                  "GAME THREAD",
                  "Game Thread"]

    discard_list = ["Post Match",
                    "Post-Match",
                    "Pre Match",
                    "Pre-Match",
                    "Post Race",
                    "Post-Race",
                    "Pre Race",
                    "Pre Game",
                    "Pre-Game",
                    "Post Game",
                    "POST GAME",
                    "Post-Game"]

    # Get sports multireddit from u/vishnumad
    sports_multi = r.get_multireddit('vishnumad', 'sports')

    # Get posts and sort by new
    posts = sports_multi.get_new(limit=100)

    # Loop through posts
    for submission in posts:
        # Get age of submission in seconds
        s_age = now_s - submission.created_utc

        # Get number of comments
        s_comments = submission.num_comments

        # Check to make sure submission age is less than 10800s (3 hours) and has at least 15 comments
        if s_age < 10800 and s_comments >= 15:
            s_title = submission.title

            # Check to make sure it's an actual game thread (not a post game thread, or discussion etc.)
            if pattern_in_title(s_title, match_list) and not pattern_in_title(s_title, discard_list):
                subreddit = submission.subreddit.__str__()
                title = (s_title + " (x-post /r/" + subreddit + ")").encode("utf-8")
                if not already_submitted(submission.short_link, url_list):
                    # Post submission to /r/RedditGameThreads if not in list
                    print "Posting submission: ", submission.short_link, " - ", title
                    try:
                        r.submit("RedditGameThreads",
                                 title,
                                 url=submission.short_link)
                    except Exception as inst:
                        print(type(inst))
                        print(inst.args)
                        print(inst)
                        pass

                else:
                    # Link has already been submitted
                    print "Already Submitted:", submission.short_link, " - ", title

except Exception as inst:
    print(type(inst))
    print(inst.args)
    print(inst)
    pass
