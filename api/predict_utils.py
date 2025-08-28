import numpy as np

def predict_top_k(model, label_encoder, input_vector, k=3):
    """
    Dự đoán top-k bệnh với xác suất từ vector đầu vào.

    Args:
        model: Mô hình đã huấn luyện (đã load từ file .pkl).
        label_encoder: LabelEncoder đã huấn luyện.
        input_vector (List[int]): Vector đặc trưng các triệu chứng (0 hoặc 1).
        k (int): Số bệnh cần dự đoán (mặc định 3).

    Returns:
        List[Tuple[str, float]]: Danh sách (bệnh, xác suất)
    """
    probs = model.predict_proba([input_vector])[0]
    top_k_indices = np.argsort(probs)[::-1][:k]

    results = []
    for i in top_k_indices:
        disease = label_encoder.inverse_transform([i])[0]
        prob = float(probs[i])
        results.append((disease, prob))

    return results
