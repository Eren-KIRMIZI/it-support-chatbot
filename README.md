# IT Support Chatbot - Akıllı Destek Yönetim Sistemi


https://github.com/user-attachments/assets/40f410b9-810d-40c4-8f2d-1a8dd6e98737


## Proje Hakkında

**IT Support Chatbot**, şirketlerin IT destek süreçlerini otomatikleştiren ve optimize eden kapsamlı bir yönetim platformudur. Sistem, chatbot ile kullanıcı sorularını anlayıp otomatik çözümler sunarken, çözülemeyen sorunları akıllı ticket sistemine yönlendirir.

### Temel Amaç

- **Kullanıcılar için**: IT sorunlarını hızlı çözmek, 7/24 destek almak
- **IT Ekibi için**: Ticket yönetimini kolaylaştırmak, SLA takibi yapmak, iş yükünü azaltmak
- **Şirket için**: Destek maliyetlerini düşürmek, müşteri memnuniyetini artırmak

### Nasıl Çalışır?

1. **Kullanıcı** web arayüzünden giriş yapar
2. **Chatbot** ile sorunu paylaşır
3. **AI** soruyu analiz eder ve intent (niyet) tespit eder
4. **FAQ Engine** bilinen çözümleri önerir
5. Çözüm yoksa otomatik **ticket** oluşturulur
6. **Admin** panelden ticket'ı yönetir
7. **SLA sistemi** kritik ticket'ları otomatik escalate eder

---

## Özellikler

### AI Destekli Chatbot
- **Intent Classification**: Kullanıcı mesajlarını makine öğrenmesi ile sınıflandırma
- **Semantic Search**: FAQ veritabanında anlamsal arama
- **Otomatik Ticket Oluşturma**: Çözülemeyen sorunları otomatik kayda alma
- **Çok Dilli Destek**: Türkçe dil desteği (genişletilebilir)

### Kullanıcı Paneli
- Sezgisel chatbot arayüzü
- Ticket oluşturma ve takip
- Gerçek zamanlı durum güncellemeleri
- Mobil uyumlu responsive tasarım
- Ticket geçmişi görüntüleme

### Admin Paneli
- Merkezi ticket yönetim dashboard'u
- Gelişmiş filtreleme (durum, priority, intent)
- Toplu işlem yapabilme
- Yorum ve not ekleme sistemi
- SLA takibi ve uyarıları
- Detaylı istatistikler ve raporlama
- Real-time veri güncelleme

### Akıllı Otomasyon
- **Rule-Based Engine**: İntent'e göre otomatik priority atama
- **SLA Management**: Süre aşımı kontrolü ve escalation
- **Auto-routing**: Sorunları doğru departmana yönlendirme
- **Priority System**: P1 (Critical) - P4 (Low) derecelendirme

---

## Sistem Mimarisi

### Genel Mimari

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │              │    │              │    │              │    │
│  │  Login Page  │───▶│     User     │    │    Admin     │    │
│  │   (HTML/JS)  │    │  Dashboard   │    │  Dashboard   │    │
│  │              │    │   (HTML/JS)  │    │   (HTML/JS)  │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                            │
                            │ HTTPS / REST API
                            │ JWT Authentication
                            │
┌────────────────────────────▼────────────────────────────────────┐
│                     APPLICATION LAYER                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              FastAPI Server (app.py)                     │ │
│  │  • REST API Endpoints                                    │ │
│  │  • Request/Response Handling                             │ │
│  │  • JWT Token Validation                                  │ │
│  │  • CORS Management                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │    Auth     │  │   Chatbot   │  │   Ticket    │           │
│  │   Module    │  │   Engine    │  │   Service   │           │
│  │  (auth.py)  │  │(chatbot.py) │  │(ticket_*.py)│           │
│  │             │  │             │  │             │           │
│  │ • JWT Auth  │  │ • NLP       │  │ • CRUD      │           │
│  │ • RBAC      │  │ • Routing   │  │ • Rules     │           │
│  │ • Bcrypt    │  │ • Response  │  │ • Status    │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Intent    │  │     FAQ     │  │     SLA     │           │
│  │ Classifier  │  │   Engine    │  │   Checker   │           │
│  │(intent_*.py)│  │ (faq_*.py)  │  │ (sla_*.py)  │           │
│  │             │  │             │  │             │           │
│  │ • TF-IDF    │  │ • Semantic  │  │ • Deadline  │           │
│  │ • LogReg    │  │ • Cosine    │  │ • Escalate  │           │
│  │ • Training  │  │ • Search    │  │ • Monitor   │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                            │
                            │ PyMongo Driver
                            │
┌────────────────────────────▼────────────────────────────────────┐
│                        DATA LAYER                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                  MongoDB Database                        │ │
│  │                                                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │    users    │  │   tickets   │  │   sessions  │    │ │
│  │  │ collection  │  │ collection  │  │ collection  │    │ │
│  │  │             │  │             │  │             │    │ │
│  │  │ • username  │  │ • ticket_id │  │ • token     │    │ │
│  │  │ • password  │  │ • user_id   │  │ • user_id   │    │ │
│  │  │ • role      │  │ • status    │  │ • expire    │    │ │
│  │  │ • email     │  │ • priority  │  │             │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  │                                                          │ │
│  │  Indexes: username, ticket_id, status, created_at       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow (Veri Akışı)

```
┌─────────────┐
│    User     │
│  Types msg  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Chatbot Engine    │
│  Receives message   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Intent Classifier   │◄───── TF-IDF Vectorization
│  Predicts intent    │◄───── Logistic Regression
└──────┬──────────────┘
       │
       ├──────────────┐
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│ FAQ Engine  │  │   Ticket    │
│ Search KB   │  │  Creation   │
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
┌─────────────────────────┐
│   Response Builder      │
│  • Answer from FAQ      │
│  • Ticket confirmation  │
│  • Intent info          │
└──────┬──────────────────┘
       │
       ▼
┌─────────────┐
│    User     │
│  Gets reply │
└─────────────┘
```

---


### Machine Learning Teknikleri

#### 1. Intent Classification (Niyet Sınıflandırma)
```python
# TF-IDF Vectorization
TfidfVectorizer() -> Metni sayısal vektöre dönüştürme

# Logistic Regression
LogisticRegression() -> Sınıflandırma modeli

# Training Process
texts + labels -> fit() -> predict()
```

**Desteklenen Intent'ler:**
- `vpn_issue` - VPN bağlantı sorunları
- `network_issue` - Ağ erişim problemleri
- `email_issue` - Email/Outlook sorunları
- `password_reset` - Şifre sıfırlama
- `ticket_request` - Genel destek talebi

#### 2. FAQ Semantic Search
```python
# Sentence Transformers (all-MiniLM-L6-v2)
SentenceTransformer() -> Cümleleri embedding'e dönüştürme

# Cosine Similarity
cosine_similarity() -> Benzerlik skoru hesaplama

# Threshold-based Matching
score >= 0.75 -> FAQ answer döndür
```

### Güvenlik

| Özellik | Implementasyon |
|---------|----------------|
| **Authentication** | JWT (JSON Web Tokens) |
| **Password Hashing** | bcrypt (salt + hash) |
| **Authorization** | Role-based access control (RBAC) |
| **CORS** | Configurable cross-origin policy |
| **Input Validation** | Pydantic models |

---

## Kullanım

### Demo Hesaplar

Sistem ilk başlatıldığında otomatik olarak demo kullanıcılar oluşturulur:

| Kullanıcı Tipi | Username | Password | Yetkiler |
|----------------|----------|----------|----------|
| **Admin** | `admin` | `admin123` | Tüm sistem yönetimi |
| **User** | `user1` | `user123` | Kendi ticket'larını yönetme |

### Kullanıcı İş Akışı

1. **Giriş Yap**: http://127.0.0.1:8000/ adresinden login ol
2. **Chatbot ile Konuş**: "VPN bağlanamıyorum" gibi bir mesaj yaz
3. **Cevap Al**: Bot FAQ'den cevap verir veya ticket oluşturur
4. **Ticket Takibi**: "Ticket'larım" sekmesinden durumu kontrol et

### Admin İş Akışı

1. **Admin Login**: `admin` / `admin123` ile giriş yap
2. **Dashboard**: Tüm ticket'ları ve istatistikleri gör
3. **Filtrele**: Durum, priority veya intent'e göre filtrele
4. **Yönet**: Ticket durumunu güncelle, yorum ekle
5. **SLA Kontrolü**: "SLA Kontrolü" butonuna bas, otomatik escalation yap

---

## Ticket Priority & SLA Kuralları

### Priority Seviyeleri

| Priority | Severity | Açıklama | SLA Süresi | Örnek |
|----------|----------|----------|------------|-------|
| **P1** | Critical | İş durduran | 1 saat | Sunucu down, network çökmesi |
| **P2** | High | İş engelleyen | 4 saat | VPN erişim sorunu |
| **P3** | Medium | İşi yavaşlatan | 24 saat | Email senkronizasyon |
| **P4** | Low | Minör sorun | 72 saat | Şifre sıfırlama |

### Otomatik Priority Atama

```python
INTENT_RULES = {
    "vpn_issue":      {"severity": "high",     "priority": "P2"},
    "network_issue":  {"severity": "critical", "priority": "P1"},
    "email_issue":    {"severity": "medium",   "priority": "P3"},
    "password_reset": {"severity": "low",      "priority": "P4"},
}
```
### SLA Escalation

- Ticket oluşturulduğunda `sla_deadline` otomatik hesaplanır
- SLA Checker her çalıştırıldığında deadline'ı geçmiş ticket'ları bulur
- Bu ticket'lar `escalated: true` olarak işaretlenir
- Status `escalated` olarak değiştirilir
