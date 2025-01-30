import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class NLPService:
    def __init__(self):
        try:
            logger.info("Initializing NLP models...")
            self.nlp = spacy.load("en_core_web_sm")
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            logger.info("NLP models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            raise

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive NLP analysis on text
        """
        try:
            # VADER Sentiment Analysis
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text)

            # spaCy Analysis
            doc = self.nlp(text)

            # Extract entities
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]

            # Extract key phrases (noun chunks)
            key_phrases = [chunk.text for chunk in doc.noun_chunks]

            # Part of speech analysis
            pos_counts = {}
            for token in doc:
                pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1

            return {
                "sentiment": {
                    "compound": sentiment_scores["compound"],
                    "positive": sentiment_scores["pos"],
                    "negative": sentiment_scores["neg"],
                    "neutral": sentiment_scores["neu"]
                },
                "entities": entities,
                "key_phrases": key_phrases,
                "pos_distribution": pos_counts,
                "sentence_count": len(list(doc.sents)),
                "word_count": len([token for token in doc if not token.is_punct])
            }

        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            raise

    def analyze_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Analyze individual segments with timing information
        """
        try:
            analyzed_segments = []

            for segment in segments:
                text = segment["text"]
                analysis = self.analyze_text(text)

                analyzed_segments.append({
                    **segment,
                    "nlp_analysis": analysis
                })

            return analyzed_segments

        except Exception as e:
            logger.error(f"Error in segment analysis: {e}")
            raise