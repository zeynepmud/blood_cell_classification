# blood_cell_classification
White blood cell classification using image processing and feature extraction techniques such as GLCM, HSV statistics, and Hu Moments.


# Kan Hücresi Sınıflandırma

Bu proje, mikroskobik beyaz kan hücresi görüntülerinin görüntü işleme ve özellik çıkarma yöntemleri kullanılarak analiz edilmesini amaçlamaktadır.

## Proje Hakkında

Projede beyaz kan hücresi görüntüleri işlenerek hücrelerin renk, doku ve şekil özellikleri çıkarılmaktadır.

Görüntü işleme aşamasında öncelikle hücrenin bulunduğu bölge tespit edilmekte ve görüntü standart bir boyuta getirilmektedir. Daha sonra GLCM, HSV renk istatistikleri ve Hu Moments kullanılarak görüntülerden çeşitli özellikler çıkarılmaktadır.

Elde edilen özellikler **ARFF** formatında tek bir dosyaya kaydedilmektedir. Bu dosya daha sonra makine öğrenmesi ve sınıflandırma çalışmalarında kullanılabilir.

## Kullanılan Veri Seti

Projede Kaggle üzerinde bulunan **Blood Cell Images** veri seti kullanılmıştır.

Veri setinde dört farklı beyaz kan hücresi sınıfı bulunmaktadır:

* Eosinophil
* Lymphocyte
* Monocyte
* Neutrophil

Veri seti yaklaşık 12.500 görüntü içermekte ve her sınıfta yaklaşık 3.000 görüntü bulunmaktadır.

**Veri seti:** [Blood Cell Images – Kaggle](https://www.kaggle.com/datasets/paultimothymooney/blood-cells)

Veri seti bu repository içerisinde yer almamaktadır. Veri seti ayrıca indirilerek proje klasörü içerisinde `dataset` adlı klasöre yerleştirilmelidir.

## Proje Yapısı

## Görüntü İşleme Aşamaları

### 1. Hücre Bölgesinin Tespiti

Görüntü içerisindeki hücrenin bulunduğu bölgeyi belirlemek için HSV renk uzayındaki **Saturation (doygunluk)** kanalı kullanılmaktadır.

Bu aşamada:

* Görüntü BGR renk uzayından HSV renk uzayına dönüştürülür.
* Saturation kanalı alınır.
* Gürültüyü azaltmak için Gaussian Blur uygulanır.
* Otsu eşikleme yöntemi ile hücre bölgesi arka plandan ayrılır.
* Konturlar tespit edilir.
* En büyük uygun kontur hücre bölgesi olarak seçilir.
* Hücrenin çevresine belirli miktarda padding eklenerek görüntü kırpılır.

Uygun bir hücre bölgesi tespit edilemediğinde görüntünün merkez bölgesi kullanılır.

### 2. Görüntü Boyutlandırma

Kırpılan hücre görüntüleri standartlaştırmak amacıyla:

```text
128 × 128
```

boyutuna getirilir.

### 3. GLCM Özellikleri

**Gray-Level Co-occurrence Matrix (GLCM)** kullanılarak görüntülerin doku özellikleri çıkarılır.

GLCM özellikleri hem gri tonlama kanalından hem de Saturation kanalından hesaplanmaktadır.

Kullanılan özellikler:

* Contrast
* Dissimilarity
* Homogeneity
* Energy
* Correlation
* ASM

GLCM hesaplamaları farklı yönlerde gerçekleştirilmekte ve elde edilen değerlerin ortalaması alınmaktadır.

### 4. HSV Renk Özellikleri

HSV renk uzayındaki üç kanal için:

* Hue
* Saturation
* Value

ortalama ve standart sapma değerleri hesaplanmaktadır.

Bu işlem sonucunda toplam **6 renk özelliği** elde edilmektedir.

### 5. Hu Moments

Hücrelerin şekil özelliklerini temsil etmek amacıyla **7 Hu Moment** değeri çıkarılmaktadır.

Hu Moments değerlerinin sayısal dağılımını daha uygun hale getirmek amacıyla logaritmik dönüşüm uygulanmaktadır.

### 6. Özelliklerin Birleştirilmesi

Tüm özellikler tek bir özellik vektöründe birleştirilerek ARFF dosyasına kaydedilmektedir.

## Çıkarılan Özellikler

| Özellik Grubu      | Özellik Sayısı |
| ------------------ | -------------: |
| Gri Tonlama GLCM   |              6 |
| Saturation GLCM    |              6 |
| HSV İstatistikleri |              6 |
| Hu Moments         |              7 |
| **Toplam**         |         **25** |

Sınıf bilgisi bu 25 özelliğin ardından son sütunda yer almaktadır.

## Veri İşleme Limiti

Kodun mevcut halinde her sınıftan **en fazla 500 görüntü** işlenmektedir.

Bu nedenle veri setinde sınıf başına yaklaşık 3.000 görüntü bulunmasına rağmen bu proje kapsamında her sınıftan en fazla 500 görüntü kullanılmaktadır.

## Kurulum

Gerekli Python kütüphanelerini yüklemek için:

```bash
pip install -r requirements.txt
```

komutu kullanılabilir.

## Kullanım

Öncelikle veri seti indirilerek proje klasöründe aşağıdaki yapıya yerleştirilmelidir:

```text
dataset/
├── eosinophil/
├── lymphocyte/
├── monocyte/
└── neutrophil/
```

Daha sonra program:

```bash
python blood_cell_classification.py
```

komutu ile çalıştırılabilir.

Program çalıştırıldığında görüntüler işlenerek:

```text
blood_cell_features.arff
```

adında bir ARFF dosyası oluşturulur.

Bu dosyada çıkarılan görüntü özellikleri ve ilgili hücre sınıfları bulunmaktadır.

## Kullanılan Teknolojiler

* Python
* OpenCV
* NumPy
* scikit-image
* GLCM
* HSV Renk Uzayı
* Otsu Eşikleme
* Hu Moments
* ARFF

## Veri Seti Kaynağı

Projede kullanılan **Blood Cell Images** veri seti Kaggle üzerinden temin edilmiştir.

[Kaggle – Blood Cell Images](https://www.kaggle.com/datasets/paultimothymooney/blood-cells)


Bu proje görüntü işleme ve özellik çıkarma aşamalarına odaklanmaktadır. 
Oluşturulan ARFF dosyası, çıkarılan özelliklerin daha sonra makine öğrenmesi algoritmalarıyla sınıflandırılmasına uygun bir veri yapısı sağlamaktadır.

