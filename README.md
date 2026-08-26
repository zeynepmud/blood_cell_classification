# blood_cell_classification
White blood cell classification using image processing and feature extraction techniques such as GLCM, HSV statistics, and Hu Moments.


# Kan Hücresi Sınıflandırma

Bu proje, mikroskobik beyaz kan hücresi görüntülerinin görüntü işleme ve makine öğrenmesi yöntemleri kullanılarak sınıflandırılmasını amaçlamaktadır.

Projede Python kullanılarak görüntülerden renk, doku ve şekil özellikleri çıkarılmış, elde edilen özellikler ARFF formatında kaydedilmiş ve WEKA kullanılarak sınıflandırma gerçekleştirilmiştir.

## Proje Akışı


Görüntüler
    ↓
Görüntü Ön İşleme
    ↓
Hücre Bölgesinin Tespiti
    ↓
Özellik Çıkarma
    ↓
ARFF Dosyası
    ↓
WEKA
    ↓
Makine Öğrenmesi ve Sınıflandırma


## Kullanılan Veri Seti

Projede Kaggle üzerinde bulunan **Blood Cell Images** veri seti kullanılmıştır.

Veri setinde dört farklı beyaz kan hücresi sınıfı bulunmaktadır:

* Eosinophil
* Lymphocyte
* Monocyte
* Neutrophil

Veri seti yaklaşık 12.500 görüntü içermekte ve sınıf başına yaklaşık 3.000 görüntü bulunmaktadır.

**Veri seti:**
[Blood Cell Images – Kaggle](https://www.kaggle.com/datasets/paultimothymooney/blood-cells)

Veri seti bu repository içerisinde yer almamaktadır. Projeyi çalıştırmak için veri setinin ayrıca indirilerek `dataset` klasörüne yerleştirilmesi gerekmektedir.

## Görüntü İşleme Aşamaları

### 1. Hücre Bölgesinin Tespiti

Hücrenin bulunduğu bölgeyi belirlemek için HSV renk uzayındaki **Saturation** kanalı kullanılmaktadır.

Bu aşamada:

* Görüntü BGR renk uzayından HSV renk uzayına dönüştürülür.
* Saturation kanalı alınır.
* Gaussian Blur ile gürültü azaltılır.
* Otsu eşikleme yöntemi uygulanır.
* Konturlar tespit edilir.
* En büyük uygun kontur hücre bölgesi olarak seçilir.
* Hücre çevresine padding eklenerek görüntü kırpılır.

Uygun bir hücre bölgesi tespit edilemediğinde görüntünün merkez bölgesi kullanılır.

### 2. Görüntü Boyutlandırma

Kırpılan görüntüler standartlaştırılmak amacıyla:


128 × 128


boyutuna getirilir.

### 3. GLCM Doku Özellikleri

**Gray-Level Co-occurrence Matrix (GLCM)** kullanılarak hem gri tonlama hem de Saturation kanallarından doku özellikleri çıkarılır.

Kullanılan özellikler:

* Contrast
* Dissimilarity
* Homogeneity
* Energy
* Correlation
* ASM

GLCM değerleri farklı yönlerde hesaplanarak ortalamaları alınır.

### 4. HSV Renk Özellikleri

HSV renk uzayındaki:

* Hue
* Saturation
* Value

kanallarının ortalama ve standart sapma değerleri hesaplanır.

Toplam **6 renk özelliği** elde edilir.

### 5. Hu Moments

Hücrelerin şekil özelliklerini temsil etmek amacıyla **7 Hu Moment** çıkarılır.

Hu Moments değerlerine logaritmik dönüşüm uygulanır.

## Çıkarılan Özellikler

| Özellik Grubu      | Özellik Sayısı |
| ------------------ | -------------: |
| Gri Tonlama GLCM   |              6 |
| Saturation GLCM    |              6 |
| HSV İstatistikleri |              6 |
| Hu Moments         |              7 |
| **Toplam**         |         **25** |

Bu 25 özelliğe ek olarak hücrenin sınıf bilgisi ARFF dosyasının son sütununda tutulur.

## ARFF Dosyası

Özellik çıkarma işlemi sonucunda:

`
blood_cell_features.arff


adında bir dosya oluşturulur.

**ARFF (Attribute-Relation File Format)**, veri madenciliği ve makine öğrenmesi uygulamalarında kullanılan bir veri formatıdır ve WEKA tarafından desteklenmektedir.

Dosyada görüntülerden çıkarılan 25 özellik ve ilgili hücre sınıfı bulunmaktadır.

## WEKA ile Sınıflandırma

Oluşturulan ARFF dosyası **WEKA (Waikato Environment for Knowledge Analysis)** kullanılarak sınıflandırma aşamasında değerlendirilmiştir.

WEKA ile:

* Veri seti incelenmiş,
* Özellikler analiz edilmiş,
* Sınıflandırma algoritmaları uygulanmış,
* Elde edilen sonuçlar karşılaştırılmıştır.

Python görüntü işleme ve özellik çıkarma aşamasında, WEKA ise elde edilen özelliklerin makine öğrenmesi algoritmalarıyla sınıflandırılmasında kullanılmıştır.

## Bulgular

Modelin geliştirme sürecinde en önemli iyileştirmelerden biri HSV renk uzayının kullanılması, diğeri ise hücre bölgesinin otomatik olarak tespit edilip kırpılmasıdır.

Bu iki yaklaşım sonucunda başlangıçtaki **%46,40 doğruluk**, final aşamasında **%88,45** seviyesine yükselmiştir.

| Aşama                             |   Doğruluk |
| --------------------------------- | ---------: |
| Başlangıç (klasik yöntem)         |     %46,40 |
| Renk uzayı iyileştirmesi          |     %63,00 |
| Şekil analizi eklenmesi           |     %85,10 |
| Akıllı kırpma + doygunluk analizi | **%88,45** |

Sınıflandırıcılar arasında **Random Forest**, **J48** karar ağacından daha başarılı sonuç vermiştir:

* J48: %76,3
* Random Forest: %87,9

En fazla karışan sınıfların **Eosinophil** ve **Neutrophil** olduğu gözlemlenmiştir. Bu sınıflar arasındaki ayrımı iyileştirmede Saturation kanalından elde edilen doku özelliklerinin önemli katkı sağladığı görülmüştür.

Sonuç olarak, görüntünün doğru bölgesinin otomatik olarak belirlenmesi ve renk, doku ve şekil özelliklerinin birlikte kullanılması sınıflandırma performansını önemli ölçüde artırmıştır.

## Veri İşleme Limiti

Kodun mevcut halinde her sınıftan **en fazla 500 görüntü** işlenmektedir.

Bu nedenle orijinal veri setinde sınıf başına yaklaşık 3.000 görüntü bulunmasına rağmen bu projede her sınıftan en fazla 500 görüntü kullanılmaktadır.

## Kurulum

Gerekli Python kütüphanelerini yüklemek için:

```bash
pip install -r requirements.txt
```

WEKA Python paketlerinden bağımsız olarak kurulmalıdır.

## Kullanım

Veri seti indirildikten sonra aşağıdaki klasör yapısına yerleştirilmelidir:

```text
dataset/
├── eosinophil/
├── lymphocyte/
├── monocyte/
└── neutrophil/
```

Daha sonra Python programı çalıştırılır:

```bash
python blood_cell_classification.py
```

Program çalıştırıldığında:

```text
blood_cell_features.arff
```

dosyası oluşturulur.

Bu dosya daha sonra WEKA'ya aktarılıp sınıflandırma işlemlerinde kullanılabilir.

## Kullanılan Teknolojiler

* Python
* OpenCV
* NumPy
* scikit-image
* WEKA
* ARFF

## Veri Seti Kaynağı

**Blood Cell Images – Kaggle**

[https://www.kaggle.com/datasets/paultimothymooney/blood-cells](https://www.kaggle.com/datasets/paultimothymooney/blood-cells)



