from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from collections import Counter
from nltk.corpus import stopwords
import nltk
import re
nltk.download('stopwords')

def generate_word_cloud(file_path, figure_file):
    with open(file_path, "r", encoding="utf-8") as file:
        # Read the entire file
        content = file.read()

        # Remove HTML tags
        content = re.sub(r'<.*?>', '', content)

        # Use jieba for Chinese word segmentation
        words = jieba.cut(content)

        # Load common Chinese stop words
        stop_words_path = 'stopwords.txt'
        with open(stop_words_path, "r", encoding="utf-8") as stop_words_file:
            stop_words = set(stop_words_file.read().splitlines())

        # Filter out stop words
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]

        # Generate the word cloud
        wordcloud = WordCloud(font_path="TaipeiSansTCBeta-Bold.ttf", width=800, height=400, background_color="white").generate(" ".join(filtered_words))

        # Display the generated image:
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")

        wordcloud.to_file(figure_file)

        plt.show()

if __name__ == "__main__":

    #輸入關鍵詞、輸出檔案名稱
    search_query = "動物救援"
    theme = search_query.replace(' ', '_')

    #初始化
    cloud_data = f"Tempfile/{theme}_cloud.txt"
    cloud_file = f"OUTPUT/{theme}_cloud.png"
    

    generate_word_cloud(cloud_data, cloud_file)
