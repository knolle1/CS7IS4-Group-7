from gensim.models import LdaMulticore
import numpy as np
from gensim.models.coherencemodel import CoherenceModel
from scipy.stats import pearsonr
 
def evaluate_model_coherence(lda_model, texts, dictionary, coherence='c_v'):
    """
    Evaluate a given model's coherence score.
    """
    coherence_model = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence=coherence)
    return coherence_model.get_coherence()

def train_and_evaluate_models(corpus, id2word, texts, num_topics_list, passes=10, random_state=42, top_n_models=3):
    """
    Train multiple LDA models, evaluate them, and select the top N models based on coherence scores.
    """
    model_list = []
    coherence_scores = []

    # Train models and calculate their coherence
    for num_topics in num_topics_list:
        model = LdaMulticore(corpus=corpus, id2word=id2word, num_topics=num_topics, 
                             passes=passes, random_state=random_state, workers=4)
        coherence_score = evaluate_model_coherence(model, texts, id2word)
        model_list.append(model)
        coherence_scores.append(coherence_score)
    
    # Select the top N models based on coherence
    top_indices = np.argsort(coherence_scores)[-top_n_models:]
    top_models = [model_list[i] for i in top_indices]
    top_scores = [coherence_scores[i] for i in top_indices]
    
    return top_models, top_scores

def process_models_and_extract_features(top_models, corpus, num_topics, id2word):
    """
    Process top models to average topics and extract feature vectors for correlation analysis.
    """
    # Initialize storage for averaged topics and feature vectors
    averaged_topics = []
    feature_vectors = np.zeros((len(corpus), num_topics))

    # Process each topic across models
    for topic_num in range(num_topics):
        topic_terms = {}
        
        # Aggregate topic distributions for feature vectors
        for i, doc_bow in enumerate(corpus):
            doc_topics_avg = np.zeros(num_topics)
            for model in top_models:
                doc_topics = dict(model.get_document_topics(doc_bow, minimum_probability=0))
                doc_topics_avg[topic_num] += doc_topics.get(topic_num, 0) / len(top_models)
            feature_vectors[i, topic_num] = doc_topics_avg[topic_num]

        # Aggregate and average topic terms for interpretability
        for model in top_models:
            for term_id, weight in model.get_topic_terms(topic_num, topn=20):
                if term_id in topic_terms:
                    topic_terms[term_id] += weight
                else:
                    topic_terms[term_id] = weight
        
        # Average the weights and sort terms
        averaged_terms = sorted([(term, weight / len(top_models)) for term, weight in topic_terms.items()],
                                key=lambda x: -x[1])[:20]
        averaged_topics.append(averaged_terms)

    # Display averaged topics
    print("\nAveraged Topics:")
    for idx, terms in enumerate(averaged_topics):
        terms_str = " + ".join([f"{weight:.3f}*{id2word[term]}" for term, weight in terms])
        print(f"Topic {idx}: {terms_str}")

    return feature_vectors

def calculate_correlation(feature_vectors, external_metrics):
    """
    Calculate the Pearson correlation between each topic's presence and external metrics.
    """
    correlations = []
    for i in range(feature_vectors.shape[1]):  # Iterate over topics
        correlation, _ = pearsonr(feature_vectors[:, i], external_metrics)
        correlations.append(correlation)
    
    return correlations

num_topics_list = [10, 15, 20]  # Explore different numbers of topics
top_n_models = 3  # Number of top models to average

# Train models and select the top N based on coherence
top_models, top_scores = train_and_evaluate_models(corpus, id2word, texts=your_preprocessed_corpus, num_topics_list=num_topics_list, top_n_models=top_n_models)

# Determine 'chosen_number_of_topics' based on your criteria. Example:
chosen_number_of_topics = num_topics_list[np.argmax(top_scores)]  # This is just an illustrative example; adjust as necessary.

# Continue with averaging model topics, feature vector extraction, and correlation calculation...
feature_vectors = process_models_and_extract_features(top_models, corpus, chosen_number_of_topics, id2word)

correlations = calculate_correlation(feature_vectors, external_metrics)

# Print correlations for analysis
for i, corr in enumerate(correlations):
    print(f"Correlation between Topic {i} and external metrics: {corr}")
