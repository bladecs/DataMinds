from django.shortcuts import render, redirect
from django.conf import settings
from pymongo import MongoClient #untuk koneksi dengan mongoDB Atlas
from django.contrib import messages #untuk pesan notif
from django.core.paginator import Paginator #untuk pagination
from datetime import datetime #untuk data waktu
client = MongoClient(settings.MONGODB_URI)
db = client['data_kelas_3aec']
collection = db['mahasiswa']


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Mencari akun sesuai dengan username
        data_user = collection.find_one({'username': username})
        if data_user:
            # Melakuakn pencocokan password
            if data_user['password'] == password:
                # Mengatur Session
                request.session['username'] = username
                jabatan = data_user.get("jabatan", None)
                request.session["jabatan"] = jabatan
                # Redirect ke function dashboard
                return redirect('dashboard')
            else:
                messages.error(request, "Incorrect password")
        else:
            messages.error(request, "User does not exist")
    return render(request, 'validation/login.html')


def logout(request):
    request.session.flush()
    return redirect("login")


def register(request):
    return render(request, 'validation/register.html')


def dashboard(request):
    # Melakukan check session
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    mahasiswa = collection.find()  # Mengambil keseluruhan data
    data = list(mahasiswa)
    sum = len(data)
    pagination = Paginator(data, 10)  # Mengambil 5 data dari list 'data'
    page = request.GET.get("page")  # Mengambil informasi tentang halaman
    # Menampilkan data dari page yang sesuai
    page_data = pagination.get_page(page)
    return render(request, 'dashboard/dashboard.html', {'data': page_data, 'user': user, 'sum':sum})


def filter(request):
    # Melakukan check session
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    if request.method == "POST":
        filter = request.POST.get("filter")
        input = request.POST.get("pencarian")
        if filter == "id" or filter == "nim":  # Ubah nilai integer menjadi string untuk regex
            mahasiswa = collection.find({
                "$expr": {
                    "$regexMatch": {
                        # Mengonversi ID ke string
                        "input": {"$toString": f"${filter}"},
                        "regex": input,
                        "options": "i"
                    }
                }
            })
        else:
            mahasiswa = collection.find(
                {filter: {"$regex": str(input), "$options": "i"}})
        data = list(mahasiswa)
        sum = len(data)
        pagination = Paginator(data, 5)
        page = request.GET.get("page")
        page_data = pagination.get_page(page)
        return render(request, 'dashboard/dashboard.html', {'data': page_data, 'user': user,'sum':sum})


def grafik(request):
    if not request.session.get('username'):
        return redirect('login')

    user = request.session["username"]

    # Pengambilan menurut tahun kelahiran
    tahun_kelahiran = [
        {
            "$group": {
                # Mengelompokkan berdasarkan tahun lahir
                # Gunakan None untuk menghindari nilai kosong
                "_id": {"$ifNull": [{"$year": "$tanggal_lahir"}, None]},
                "count": {"$sum": 1}  # Menghitung jumlah mahasiswa per tahun
            }
        },
        {
            # Mengurutkan berdasarkan tahun lahir secara ascending
            "$sort": {"_id": 1}
        }
    ]
    result_tgl = list(collection.aggregate(tahun_kelahiran))
    years = [data["_id"]
             for data in result_tgl if data["_id"] is not None]  # Filter None
    counts_tgl = [data["count"]
                  # Filter None
                  for data in result_tgl if data["_id"] is not None]

    # Pengambilan menurut tempat lahir
    tempat_lahir = [
        {
            "$group": {
                # Gunakan None untuk menghindari nilai kosong
                "_id": {"$ifNull": ['$tempat_lahir', None]},
                "count": {"$sum": 1}
            }
        },
        {
            # Mengurutkan berdasarkan tempat lahir secara ascending
            "$sort": {"_id": 1}
        }
    ]
    result_tl = list(collection.aggregate(tempat_lahir))
    place = [data1["_id"]
             for data1 in result_tl if data1["_id"] is not None]  # Filter None
    counts_tl = [data1["count"]
                 # Filter None
                 for data1 in result_tl if data1["_id"] is not None]

    # Pengambilan menurut gender (jenis_kelamin)
    jenis_kelamin = [
        {
            "$group": {
                # Gunakan None untuk menghindari nilai kosong
                "_id": {"$ifNull": ['$jenis_kelamin', None]},
                "count": {"$sum": 1}  # Menghitung jumlah mahasiswa per gender
            }
        },
        {
            # Mengurutkan berdasarkan jenis kelamin secara ascending
            "$sort": {"_id": 1}
        }
    ]
    result_gender = list(collection.aggregate(jenis_kelamin))
    genders = [data2["_id"]
               # Filter None
               for data2 in result_gender if data2["_id"] is not None]
    counts_gender = [data2["count"]
                     # Filter None
                     for data2 in result_gender if data2["_id"] is not None]

    # Context untuk template
    context = {
        'user': user,
        'years': years,
        'counts_tgl': counts_tgl,
        'place': place,
        'counts_tl': counts_tl,
        'genders': genders,
        'counts_gd': counts_gender
    }
    return render(request, 'dashboard/grafik.html', context)


def profile(request):
    user = request.session['username']
    data_diri = collection.find_one({'username': user})
    # Ambil tanggal_lahir dari database
    tgl_lahir = data_diri.get('tanggal_lahir', '')
    if tgl_lahir:
        tahun = tgl_lahir.year
        bulan = tgl_lahir.month
        hari = tgl_lahir.day
    else:
        # Jika tanggal_lahir tidak ada atau kosong
        tahun, bulan, hari = None, None, None
    data_diri['jenis_kelamin'] = data_diri.get('jenis_kelamin', None)
    data_diri['year'] = tahun
    data_diri['month'] = bulan
    data_diri['date'] = hari
    return render(request, 'dashboard/profile.html', {'data': data_diri, 'user': user})


def update_profile(request, nim):
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    if request.method == 'POST':
        try:
            # Ambil data dari form
            nama = request.POST.get('name')
            jenis_kelamin = request.POST.get('genders')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            tempat_lahir = request.POST.get('place')
            no_telp = request.POST.get('phone')
            date = int(request.POST.get('date'))
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            # Update data
            collection.update_one(
                {'id': nim},
                {
                    "$set": {
                        "nama": nama,
                        "jenis_kelamin": jenis_kelamin,
                        "username": username,
                        "password": password,
                        "tempat_lahir": tempat_lahir,
                        "no_telp": no_telp,
                        "email": email,
                        "tanggal_lahir": datetime(year, month, date),
                    }
                }
            )
            # Jika berhasil
            messages.success(request, 'Data updated successfully!')
        except Exception as e:
            # Jika terjadi error
            messages.error(request, f'Error updating data: {str(e)}')
    return redirect("profile")


def update(request, nim):
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    if request.method == 'POST':
        try:
            # Ambil data dari form
            nama = request.POST.get('name')
            jenis_kelamin = request.POST.get('genders')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            tempat_lahir = request.POST.get('place')
            no_telp = request.POST.get('phone')
            date = int(request.POST.get('date'))
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            # Update data
            collection.update_one(
                {'id': nim},
                {
                    "$set": {
                        "nama": nama,
                        "jenis_kelamin": jenis_kelamin,
                        "username": username,
                        "password": password,
                        "tempat_lahir": tempat_lahir,
                        "no_telp": no_telp,
                        "email": email,
                        "tanggal_lahir": datetime(year, month, date),
                    }
                }
            )
            # Jika berhasil
            messages.success(request, 'Data updated successfully!')
        except Exception as e:
            # Jika terjadi error
            messages.error(request, f'Error updating data: {str(e)}')
    return redirect("dashboard")


def delete(request, nim):
    if not request.session.get('username'):
        return redirect('login')
    # Menghapus data mahasiswa berdasarkan NIM
    result = collection.delete_one({'id': int(nim)})
    if result.deleted_count > 0:
        messages.success(request, 'Data deleted successfully!')
    else:
        messages.error(request, 'Error deleting data.')
    return redirect('dashboard')


def edit(request, nim):
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    nim_convert = int(nim)
    # Mengambil data mahasiswa berdasarkan NIM
    mahasiswa = collection.find_one({'id': nim_convert})
    tgl_lahir = mahasiswa.get('tanggal_lahir', '')
    if tgl_lahir:
        tahun = tgl_lahir.year
        bulan = tgl_lahir.month
        hari = tgl_lahir.day
    else:
        # Jika tanggal_lahir tidak ada atau kosong
        tahun, bulan, hari = None, None, None
    mahasiswa['jenis_kelamin'] = mahasiswa.get('jenis_kelamin', None)
    mahasiswa['year'] = tahun
    mahasiswa['month'] = bulan
    mahasiswa['date'] = hari
    if mahasiswa:
        return render(request, 'dashboard/edit.html', {'data': mahasiswa, 'user': user})
    else:
        messages.error(request, "Data not found")
        return redirect('dashboard')

def input(request):
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    return render(request, "dashboard/input.html",{'user':user})

def input_data(request):
    if not request.session.get('username'):
        return redirect('login')
    user = request.session["username"]
    if request.method == 'POST':
        try:
            # Ambil data dari form
            nama = request.POST.get('name')
            nim = int(request.POST.get("nim"))
            jenis_kelamin = request.POST.get('genders')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            tempat_lahir = request.POST.get('place')
            no_telp = request.POST.get('phone')
            date = int(request.POST.get('date'))
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            # Insert data
            collection.insert_one(
                {
                    "id": nim,
                    "nama": nama,
                    "jenis_kelamin": jenis_kelamin,
                    "username": username,
                    "password": password,
                    "tempat_lahir": tempat_lahir,
                    "no_telp": no_telp,
                    "email": email,
                    "tanggal_lahir": datetime(year, month, date),
                }
            )
            # Jika berhasil
            messages.success(request, 'Data updated successfully!')
        except Exception as e:
            # Jika terjadi error
            messages.error(request, f'Error updating data: {str(e)}')
    return redirect("input")

def schedule(request):
    return render(request,'dashboard/schedule.html')

def attendance(request):
    return render(request,'dashboard/attendance.html')
