
# -----------------------------------------------------------
# GÖRÜNTÜ İŞLEME
# Konu: Kan Hücrelerinin (Lökosit) Sınıflandırılması
# -----------------------------------------------------------

import os
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops


# --- AYARLAR ---
DATASET_PATH = "dataset"
OUTPUT_FILE = "blood_cell_features.arff"
IMG_SIZE = (128, 128)


def get_smart_crop(img):
    """
    Görüntü içerisindeki temel hücre bölgesini tespit ederek kırpar.

    Hücre bölgesi HSV renk uzayındaki doygunluk (Saturation) kanalı
    kullanılarak belirlenir. Gürültüyü azaltmak için bulanıklaştırma,
    hücre bölgesini arka plandan ayırmak için ise Otsu eşikleme uygulanır.

    Uygun bir hücre bölgesi tespit edilemediğinde görüntünün merkez
    bölgesi varsayılan olarak kullanılır.
    """

    # Görüntüyü BGR renk uzayından HSV renk uzayına dönüştür.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV görüntüsünden doygunluk kanalını al.
    saturation = hsv[:, :, 1]

    # Eşikleme öncesinde görüntüdeki gürültüyü azalt.
    blurred = cv2.GaussianBlur(saturation, (5, 5), 0)

    # Otsu yöntemi ile hücre bölgesini arka plandan ayır.
    _, thresh = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Eşiklenmiş görüntü üzerindeki dış konturları tespit et.
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Uygun bir kontur bulunamazsa görüntünün merkez bölgesini kullan.
    if len(contours) == 0:
        h, w = img.shape[:2]
        return img[
            h // 4:3 * h // 4,
            w // 4:3 * w // 4
        ]

    # En büyük konturu ana hücre bölgesi olarak kabul et.
    c = max(contours, key=cv2.contourArea)

    # Hücre bölgesini çevreleyen dikdörtgenin koordinatlarını belirle.
    x, y, w, h = cv2.boundingRect(c)

    # Tespit edilen bölge çok küçükse merkez bölgeyi kullan.
    if w < 20 or h < 20:
        h_img, w_img = img.shape[:2]
        return img[
            h_img // 4:3 * h_img // 4,
            w_img // 4:3 * w_img // 4
        ]

    # Hücre çevresine ek alan bırakmak için dolgu miktarını belirle.
    padding = 10
    h_img, w_img = img.shape[:2]

    # Kırpma koordinatlarını görüntü sınırları içerisinde tut.
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(w_img, x + w + padding)
    y2 = min(h_img, y + h + padding)

    # Hücre bölgesini görüntüden kırp.
    cropped_cell = img[y1:y2, x1:x2]

    return cropped_cell


def extract_glcm_features(channel):
    """
    Gri Seviye Eş Oluşum Matrisi (GLCM) kullanarak doku özelliklerini
    çıkarır.

    Farklı yönlerde hesaplanan GLCM özelliklerinin ortalaması alınarak
    her özellik için tek bir değer elde edilir.
    """

    # Farklı yönlerde GLCM matrisi oluştur.
    glcm = graycomatrix(
        channel,
        distances=[1],
        angles=[
            0,
            np.pi / 4,
            np.pi / 2,
            3 * np.pi / 4
        ],
        levels=256,
        symmetric=True,
        normed=True
    )

    features = []

    # Kullanılacak doku özelliklerini belirle.
    props = [
        'contrast',
        'dissimilarity',
        'homogeneity',
        'energy',
        'correlation',
        'ASM'
    ]

    # Her özellik için farklı yönlerdeki değerlerin ortalamasını hesapla.
    for prop in props:
        val = graycoprops(glcm, prop).mean()
        features.append(val)

    return features


def extract_hsv_stats(image_bgr):
    """
    Görüntünün HSV kanallarına ait ortalama ve standart sapma
    değerlerini hesaplar.

    Ayrıca sonraki doku analizlerinde kullanılmak üzere
    doygunluk kanalını döndürür.
    """

    # Görüntüyü BGR renk uzayından HSV renk uzayına dönüştür.
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    features = []

    # Hue, Saturation ve Value kanallarını ayrı ayrı işle.
    for i in range(3):
        channel = hsv[:, :, i]

        # Kanalın ortalama değerini ekle.
        features.append(np.mean(channel))

        # Kanalın standart sapmasını ekle.
        features.append(np.std(channel))

    # Özellikleri ve doygunluk kanalını döndür.
    return features, hsv[:, :, 1]


def main():
    print("Hücre tespiti ve özellik çıkarma işlemi başlatılıyor...")

    # Veri setindeki sınıf klasörlerini belirle.
    classes = [
        d for d in os.listdir(DATASET_PATH)
        if os.path.isdir(os.path.join(DATASET_PATH, d))
    ]

    # ARFF dosyasını oluştur ve özellik bilgilerini yaz.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        # ARFF veri kümesi adını tanımla.
        f.write("@RELATION blood_cell_classification\n\n")

        # GLCM ile çıkarılacak doku özelliklerini belirle.
        glcm_props = [
            'contrast',
            'dissimilarity',
            'homogeneity',
            'energy',
            'correlation',
            'ASM'
        ]

        # Gri kanal için GLCM özelliklerini tanımla.
        for name in glcm_props:
            f.write(f"@ATTRIBUTE gray_{name} NUMERIC\n")

        # Doygunluk kanalı için GLCM özelliklerini tanımla.
        for name in glcm_props:
            f.write(f"@ATTRIBUTE sat_{name} NUMERIC\n")

        # HSV kanallarının ortalama ve standart sapma özelliklerini tanımla.
        hsv_names = ['Hue', 'Saturation', 'Value']

        for c in hsv_names:
            f.write(f"@ATTRIBUTE {c}_mean NUMERIC\n")
            f.write(f"@ATTRIBUTE {c}_std NUMERIC\n")

        # Şekil özellikleri için yedi Hu Momentini tanımla.
        for i in range(7):
            f.write(f"@ATTRIBUTE hu_moment_{i + 1} NUMERIC\n")

        # Sınıf bilgisini veri setindeki klasör adlarından oluştur.
        f.write(f"@ATTRIBUTE class {{{','.join(classes)}}}\n\n")

        # Veri bölümünü başlat.
        f.write("@DATA\n")

        # Her sınıf için görüntüleri işle.
        for label in classes:
            folder_path = os.path.join(DATASET_PATH, label)

            # Her sınıftan en fazla 500 görüntü kullan.
            images = os.listdir(folder_path)[:500]

            print(f"'{label}' sınıfı işleniyor...")

            for img_name in images:

                # Yalnızca desteklenen görüntü formatlarını işle.
                if not img_name.lower().endswith(
                    ('.png', '.jpg', '.jpeg')
                ):
                    continue

                path = os.path.join(folder_path, img_name)

                # Görüntüyü dosyadan oku.
                img = cv2.imread(path)

                # Görüntü okunamazsa sonraki görüntüye geç.
                if img is None:
                    continue

                # Görüntü içerisindeki hücre bölgesini tespit ederek kırp.
                img = get_smart_crop(img)

                # Tüm görüntüleri aynı boyuta getir.
                img = cv2.resize(img, IMG_SIZE)

                # Görüntüyü gri tonlamaya dönüştür.
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Gri kanal üzerinden GLCM özelliklerini çıkar.
                feat_gray_glcm = extract_glcm_features(gray)

                # HSV renk istatistiklerini ve doygunluk kanalını elde et.
                feat_hsv, saturation_channel = extract_hsv_stats(img)

                # Doygunluk kanalı üzerinden GLCM özelliklerini çıkar.
                feat_sat_glcm = extract_glcm_features(saturation_channel)

                # Doygunluk kanalını Otsu yöntemiyle eşikle.
                _, thresh = cv2.threshold(
                    saturation_channel,
                    0,
                    255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )

                # Eşiklenmiş görüntü üzerinden görüntü momentlerini hesapla.
                moments = cv2.moments(thresh)

                # Görüntünün Hu Momentlerini elde et.
                hu = cv2.HuMoments(moments).flatten()

                # Hu Momentlerini logaritmik dönüşüm ile ölçeklendir.
                feat_hu = [
                    -1 * np.sign(h) * np.log10(np.abs(h) + 1e-10)
                    for h in hu
                ]

                # Tüm özellikleri tek bir özellik vektöründe birleştir.
                all_feats = (
                    feat_gray_glcm
                    + feat_sat_glcm
                    + feat_hsv
                    + feat_hu
                )

                # Özellikleri virgülle ayırarak ARFF dosyasına yaz.
                line = ",".join([str(x) for x in all_feats])
                f.write(f"{line},{label}\n")

    print(f"Özellik çıkarma işlemi tamamlandı: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()