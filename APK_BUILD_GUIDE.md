# How to Convert Campus Gate Web App into an Android APK File
### Complete Step-by-Step Guide for Creating `.apk` Installer Files

This guide explains how to convert your live web application into an installable **Android `.apk` file** that you can send directly to security guards, principals, or clients via WhatsApp or Google Drive.

---

## ⚡ Method 1: PWABuilder (Recommended - 100% Free & Official Microsoft Tool)

[PWABuilder.com](https://www.pwabuilder.com) converts PWA-enabled web applications into native Android `.apk` / `.aab` packages in **1 minute**.

### Step-by-Step Instructions:

1. **Deploy your Web App live**:
   - Ensure your app is live on Render (e.g. `https://campus-gate-system.onrender.com`) or active via localtunnel (`https://sixty-islands-learn.loca.lt`).

2. **Open PWABuilder**:
   - Go to [pwabuilder.com](https://www.pwabuilder.com).
   - Enter your live URL in the box (e.g. `https://campus-gate-system.onrender.com`).
   - Click **Start**.

3. **Generate Android Package**:
   - PWABuilder will audit your app and show green checkmarks for Manifest and Service Worker.
   - Click **Package for Store** $\rightarrow$ Select **Android**.
   - Click **Generate / Download APK**.

4. **🎉 Done!**
   - You will get a downloadable `.apk` file (e.g. `CampusGate.apk`).
   - Send this `.apk` file via WhatsApp to guards or clients to install directly on their Android smartphones or tablets!

---

## 📲 Method 2: Instant Android Installation (No APK Download Needed!)

Because we built PWA support directly into the web app:

1. Guards open the website URL on Chrome on their Android phone or tablet.
2. A top banner automatically appears: **"Install Campus Gate App"**.
3. Clicking **Install App** adds the app directly onto their phone's home screen with its own App Icon and standalone full-screen window!

---

## 🛠️ Method 3: Website 2 APK / WebView Builder

1. Download **Website 2 APK Builder** or use online tools like [webintoapp.com](https://www.webintoapp.com) or [gonative.io](https://gonative.io).
2. Enter App Name: `Campus Gate Security`
3. Enter Web URL: `https://your-app.onrender.com`
4. Upload Logo / Icon: Upload campus shield logo.
5. Click **Create APK**.

---

## 💻 Method 4: Native Android APK using Android Studio (WebView App)

If you want to build a fully customizable native Android APK using **Android Studio**:

### Step 1: Create a New Android Studio Project
1. Open **Android Studio** $\rightarrow$ Click **New Project**.
2. Select **Empty Views Activity** $\rightarrow$ Click **Next**.
3. Set Name: `Campus Gate Security`
4. Set Package Name: `com.campusgate.app`
5. Language: **Java** (or **Kotlin**), Minimum SDK: **API 24 (Android 7.0)**.
6. Click **Finish**.

### Step 2: Add Internet Permission (`AndroidManifest.xml`)
Open `app/src/main/AndroidManifest.xml` and add this line inside `<manifest>`:
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### Step 3: Configure UI (`activity_main.xml`)
Open `app/src/main/res/layout/activity_main.xml` and replace its content with:
```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</RelativeLayout>
```

### Step 4: Write WebView Logic (`MainActivity.java`)
Open `app/src/main/java/com/campusgate/app/MainActivity.java` and replace with:
```java
package com.campusgate.app;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);

        webView.setWebViewClient(new WebViewClient());
        
        // Replace with your live Render URL or local tunnel URL
        webView.loadUrl("https://your-app.onrender.com");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
```

### Step 5: Build `.apk` File
1. In Android Studio top menu, click **Build** $\rightarrow$ **Build Bundle(s) / APK(s)** $\rightarrow$ **Build APK(s)**.
2. Android Studio will compile the code. When finished, a notification appears at bottom right: **"APK(s) generated successfully."**
3. Click **locate** to open the folder containing `app-debug.apk`.
4. Rename `app-debug.apk` to `CampusGate.apk` and share it with your clients!

---

## 📋 Distribution Checklist for Client Sale

When selling the app to a college:
- Send the `.apk` file via WhatsApp or email.
- Guards open the `.apk` file on their Android phone/tablet, click **Install**, and launch the app from their phone home screen!

