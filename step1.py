import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

def get_video_ids_by_search(youtube, search_query, video_results, video_priority):

    try:
        search_response = youtube.search().list(
            q=search_query,
            type="video",
            part="id",
            maxResults=video_results,
            order = video_priority
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        return video_ids
    
    except HttpError as e:
        print(f"Error searching for videos: {e}")
        return []

def get_video_details(youtube, video_id):  

    try:
        videos_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        snippet = videos_response["items"][0]["snippet"]
        title = videos_response["items"][0]["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        published_at = snippet["publishedAt"]

        return title, url, published_at
    
    except HttpError as e:
        print(f"Error retrieving video details for video {video_id}: {e}")
        return None, None, None

def get_word_frequency(youtube, video_id, comment_results, comments_prioritiy):

    try:
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        if 'items' in video_response and video_response['items']:
            if not video_response['items'][0]['snippet'].get('commentsAllowed', True):
                return Counter()

        comments_response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=comment_results,
            order= comments_prioritiy
        ).execute()

        comments = []
        for comment in comments_response.get("items", []):
            text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)

        # Combine all comments into a single string
        all_comments = ' '.join(comments)

        # Tokenize the comments and filter out stopwords
        words = all_comments.split()
        stop_words = set(stopwords.words('english'))
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]

        # Count filtered word frequencies
        word_counts = Counter(filtered_words)

        return word_counts
    
    except HttpError as e:
        return Counter()

def get_youtube_comments_and_timeline(youtube, video_id, comment_results, comments_prioritiy, need_author):

    try:
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        if 'items' in video_response and video_response['items']:
            if not video_response['items'][0]['snippet'].get('commentsAllowed', True):
                print(f"Comments are disabled for the video with ID: {video_id}")
                return []

        comments_response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=comment_results,
            order= comments_prioritiy
        ).execute()

        comments = []
        timeline = []
        comment_and_timeline = []
        for comment in comments_response.get("items", []):
            author = comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
            text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            time = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            
            comments.append(f"{author}: {text}\n")
            timeline.append(f"{time}\n")
            if need_author == 1:
                comment_and_timeline.append(f"{time}\n{author}: {text}\n")
            else:
                comment_and_timeline.append(f"{time}\n{text}\n")

        return comments, timeline, comment_and_timeline
    
    except HttpError as e:
        print(f"Error retrieving comments for video")
        return [], [], []

if __name__ == "__main__":

    #TO-DO: 輸入關鍵詞、輸出檔案名稱
    search_query = "YOUR_QUERY"
    theme = search_query.replace(' ', '_')

    #TO-DO: 爬取資料ㄋㄔㄛ的優先順序
    video_priority = "relevance" #"searchSortUnspecified", "date", "rating", "viewCount", "relevance", "title", "videoCount"
    comments_prioritiy = "relevance" #"orderUnspecified", "time", "relevance" 
    need_author = 0; #需不需要爬取留言者名稱
    
    #TO-DO: 輸入API
    api_key = "YOUR_API"
    video_results = 50
    comment_results = 100

    #TO-DO: 初始化
    cloud_data = f"Tempfile/{theme}_cloud.txt"
    timeline_data = f"Tempfile/{theme}_timeline.txt"
    video_data = f"Tempfile/{theme}_video.txt"
    all_data = f"ALL/{theme}_all.md"

    youtube = build("youtube", "v3", developerKey=api_key)
    video_ids = get_video_ids_by_search(youtube, search_query, video_results, video_priority)
    all_word_counts = Counter()
    all_comments = []  # List to store all comments

    with open(cloud_data, "w", encoding="utf-8") as file1, open(timeline_data, "w", encoding="utf-8") as file2, open(video_data, "w", encoding="utf-8") as file3, open(all_data, "w", encoding="utf-8") as file4:
        for video_id in video_ids:
            title, url, published_at = get_video_details(youtube, video_id)
            if title and url:
                print()
                print(f"影片的標題：{title}")
                print(f"影片的連結：{url}")

                word_counts = get_word_frequency(youtube, video_id, video_results, comments_prioritiy)
                all_word_counts += word_counts

                comments, timeline, comment_and_timeline = get_youtube_comments_and_timeline(youtube, video_id, video_results, comments_prioritiy, need_author)
                all_comments.extend(comments)

                print(f"{comments}\n\n")
                
                file1.writelines(comments)
                file1.write("\n\n")
                
                file2.writelines(timeline)
                file2.write("\n\n")
                
                file3.write(f"影片發布時間：{published_at}\n影片標題：{title}\n影片連結:{url}\n\n")
                
                file4.write(f"影片發布時間：{published_at}\n影片標題：{title}\n影片連結:{url}\n")
                file4.writelines(comment_and_timeline)
                file4.write("\n\n")

        # Output total number of comments
        total_comments = len(all_comments)
        print(f"\n總影片數量：{video_results}\n總留言數量：{total_comments}")
        file4.write(f"\n總留言數量：{total_comments}")
        
        #print("高頻率出現字詞及其次數：")
        
        stop_words_path = 'stopwords.txt'
        with open(stop_words_path, "r", encoding="utf-8") as stop_words_file:
            stop_words = set(stop_words_file.read().splitlines())

        for word, count in all_word_counts.most_common():
            if count > 50 and word not in stop_words:
                file4.write(f"{word}: {count}")
                #print(f"{word}: {count}")  