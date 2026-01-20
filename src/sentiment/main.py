from textblob import TextBlob
 
def get_sentiment( text):
        polarity = TextBlob(text).sentiment.polarity
        if polarity < -0.3:
            return "negative"
        elif polarity > 0.3:
            return "positive"
        else:
            return "neutral"