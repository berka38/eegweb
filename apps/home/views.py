# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import matplotlib
matplotlib.use('Agg')
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from apps.home.models import TextFile
from django.db.models import Sum
from django.contrib.auth.models import User
from apps.authentication.models import Profile
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from scipy.fft import fft
from mpl_toolkits.mplot3d import Axes3D
import os
from django.conf import settings





from django.core.files.storage import FileSystemStorage

datat = {
    "prod":[
        {
            "name":"deneme",
            "position":"dada",
            "office": "dalton"
        },
        {
            "name":"deneme1",
            "position":"dad1",
            "office": "dalton1"
        },
        {
            "name":"deneme2",
            "position":"dada2",
            "office": "dalton2"
        },
        {
            "name":"deneme3",
            "position":"dada3",
            "office": "dalton3"
        },
    ]
}

@login_required(login_url="/login/")
def index(request):

    # profile, created = Profile.objects.get_or_create(user=request.user)
        
        # `balance` değerini güncelle ve profile kaydet
    # profile.balance += 10
    # profile.save()
    #spends = Profile.spends.all()
    profile = Profile.objects.get(user=request.user)
    #for spend in profile.spends.all():
    #   print(f"Tarih: {spend.Date}, Açıklama: {spend.About}, Harcama: {spend.Spend} TL")   

    today = timezone.now().date()

   


    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "UploadFileEEG":
            Title = request.POST["Title"]
            File = request.FILES.get('formFile')
            print(File)
            SignalUpload = TextFile.objects.create(Title = Title, file = File ,user=profile.user)
            SignalUpload.save()

            

        return redirect('/')



    # Sayfa render edilirken, kullanıcı bilgileri burada alınabilir
    profile = Profile.objects.get(user=request.user)
    
    dataas= TextFile.objects.filter(user=profile.user)
    
    
    context = {
    'datas': datat,
    'profile' : profile,
    'usersCount':User.objects.count(),
    'totalData':TextFile.objects.count(),
    'segment': 'index',
    'files': dataas,

    }
    

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))





def job_detail(request):
    profile = Profile.objects.get(user=request.user)
    try:
        # ID'ye göre ilgili işi getir veya 404 döndür
        context = {
            'prof': profile,

        
        }
        return render(request, 'home/jobdetail.html', context)
    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(request))
    


def generate_graphs(request):
    # Kaydedilecek görüntülerin yolu
    img_dir = os.path.join("apps/static", 'myapp/static/images')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    # Initialize parameters
    samplerate = 500  # in Hz
    N = 1024  # data length
    sinefreq1 = 20  # in Hz
    sinefreq2 = 60  # in Hz
    nfft = 64  # window size for each segment
    noverlap = nfft // 2  # number of overlapping points (50%)

    # Generate simulated signals with step changes in frequency
    ts = np.arange(1, N//4 + 1) / samplerate  # time axis for each segment
    data = np.concatenate([np.zeros(N//4), 
                           np.sin(2 * np.pi * sinefreq1 * ts), 
                           np.sin(2 * np.pi * sinefreq2 * ts), 
                           np.zeros(N//4)])

    taxis = np.arange(1, N+1) / samplerate  # time axis for whole data length

    # --- Plot the signal ---
    plt.figure()
    plt.plot(taxis, data)
    plt.xlim([taxis[0], taxis[-1]])
    plt.xlabel('Time (s)')
    plt.title('Signal with Step Changes in Frequency')
    plt.savefig(os.path.join(img_dir, 'plot_signal.png'))
    plt.close()

    # --- FFT Spectrum ---
    data_freq = fft(data, N)
    Mag = np.abs(data_freq)
    faxis = np.linspace(0, samplerate/2, N//2 + 1)

    plt.figure()
    plt.plot(faxis, Mag[:N//2 + 1])
    plt.title('Spectral Analysis (FFT)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.savefig(os.path.join(img_dir, 'plot_fft.png'))
    plt.close()

    # --- Spectrogram ---
    f, t, Sxx = spectrogram(data, fs=samplerate, window='hamming', nperseg=nfft, noverlap=noverlap, nfft=nfft)

    plt.figure()
    plt.pcolormesh(t, f, np.abs(Sxx), shading='auto')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Spectrogram (Surface Plot)')
    plt.colorbar(label='Magnitude')
    plt.savefig(os.path.join(img_dir, 'plot_spectrogram.png'))
    plt.close()

    # --- 3D Surface Plot ---
    plt.figure()
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    X, Y = np.meshgrid(t, f)
    ax.plot_surface(X, Y, np.abs(Sxx), cmap='viridis', edgecolor='none')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_zlabel('Magnitude')
    plt.title('Spectrogram (3D Surface Plot)')
    plt.savefig(os.path.join(img_dir, 'plot_surface.png'))
    plt.close()

    # Görselleri şablona gönder
    context = {
        'plots': [
            'myapp/static/images/plot_signal.png',
            'myapp/static/images/plot_fft.png',
            'myapp/static/images/plot_spectrogram.png',
            'myapp/static/images/plot_surface.png'
        ],
        'name': [
            'Frekans',
            'spektral analiz',
            'spectogram',
            'spectogram 3d'
        ],
          # Medya yolu şablona dahil et
    }

    return render(request, 'home/graph.html', context)