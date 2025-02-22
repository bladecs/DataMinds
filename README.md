# DataMinds

# Django + PyMongo + MongoDB Atlas

## 1. Persiapan Awal
Pastikan Anda sudah menginstal Python dan pip. Jika belum, unduh dan instal dari [Python Official Site](https://www.python.org/downloads/).

## 2. Instalasi Django dan PyMongo

Jalankan perintah berikut untuk menginstal Django dan PyMongo:

```sh
pip install django pymongo dnspython
```

## 3. Membuat Proyek Django

Buat proyek Django baru dengan perintah:

```sh
django-admin startproject myproject
cd myproject
```

## 4. Membuat Akun dan Cluster di MongoDB Atlas

1. **Buka MongoDB Atlas**: Kunjungi [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) dan daftar jika belum memiliki akun.
2. **Buat Cluster**:
   - Pilih penyedia cloud (AWS, GCP, atau Azure).
   - Pilih region yang diinginkan.
   - Pilih tier yang gratis (M0 Free Tier).
   - Klik **Create Cluster**.
3. **Buat Database dan Koleksi**:
   - Masuk ke **Database** > **Browse Collections**.
   - Klik **Add My Own Data** dan buat database serta koleksi baru.
4. **Dapatkan Connection String**:
   - Klik **Connect** > **Connect your application**.
   - Salin connection string dengan format berikut:
     ```
     mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority
     ```
   - Gantilah `<username>`, `<password>`, dan `<dbname>` dengan informasi yang sesuai.

## 5. Konfigurasi Django untuk MongoDB

Buka file `settings.py` dalam proyek Django dan tambahkan konfigurasi database:

```python
MONGODB_URI = os.getenv('MONGODB_URI',"isi sama link mongo atlas kalian")
client = MongoClient(MONGODB_URI)
db = client['data_kelas_3aec']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Gantilah `<dbname>`, `<username>`, dan `<password>` sesuai dengan kredensial yang telah dibuat di MongoDB Atlas.

## 6. Menjalankan Server Django

Setelah konfigurasi selesai, jalankan server Django dengan perintah:

```sh
python manage.py runserver
```

Akses proyek di browser melalui `http://127.0.0.1:8000/`.

## 7. Menyimpan ke GitHub

1. **Inisialisasi Git**:

   ```sh
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Buat Repository di GitHub**:
   - Masuk ke [GitHub](https://github.com/) dan buat repository baru.
   - Salin URL repository.

3. **Push ke GitHub**:

   ```sh
   git remote add origin <repo_url>
   git branch -M main
   git push -u origin main
   ```

**Catatan**: Jangan lupa menambahkan `.env` atau menggunakan `settings.py` yang aman untuk menyembunyikan kredensial database.

## 8. Kesimpulan
Dengan langkah-langkah ini, Django telah dikonfigurasi untuk menggunakan MongoDB Atlas melalui PyMongo. Proyek juga telah berhasil diunggah ke GitHub.

