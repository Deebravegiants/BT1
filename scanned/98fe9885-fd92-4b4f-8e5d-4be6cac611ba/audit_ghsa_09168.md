# [M] FacturaScripts Vulnerable to Unstripped Image Metadata (EXIF) Leakage via Library Module File Upload/Download

## Summary
Severity: Medium
Advisory: GHSA-q7f2-rv22-2xgr
CVE: CVE-2026-27892
CWE: CWE-200, CWE-212
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-q7f2-rv22-2xgr
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
## Summary

**Fectura Scripts** is an open-source ERP application, a **sensitive information disclosure vulnerability** was identified in the **Library** module's image upload and download pipeline. The application fails to strip EXIF and other embedded metadata from user-uploaded image files before storing them and serving them for download. As a result, any authenticated user who downloads an image from the Library can extract the original uploader's **GPS coordinates, device information, timestamps, embedded comments/notes, thumbnail previews, and other personally identifiable information (PII)** preserved in the image metadata.

This vulnerability carries significant real-world impact: **an employee uploading a photo taken at their home inadvertently discloses their precise home address to every user with Library download access.**

---

## Affected Functionality Overview

Fectura Scripts exposes image upload capabilities across several modules (e.g., email composition, profile settings, etc.). During testing, the **Library section** was identified as the only module that provides:

- **Full image upload** (unrestricted image types observed)
- **Persistent storage** of uploaded files
- **Direct download** capability for any authenticated user with access
- **No server-side metadata sanitization** at any point in the pipeline (upload, storage, or delivery)

Other modules (e.g., email attachments) were also tested but either did not render images or had limited upload/download exposure.

---

## Technical Background

### What Is EXIF/Image Metadata?

Most modern image formats (JPEG, TIFF, PNG with ancillary chunks, HEIC, WebP with XMP) embed metadata automatically at creation time. This metadata can include:

| Metadata Category | Example Fields | Privacy Risk |
|---|---|---|
| **GPS / Geolocation** | GPSLatitude, GPSLongitude, GPSAltitude, GPSTimestamp | **Critical** — reveals exact physical location |
| **Device Information** | Make, Model, Software, LensModel | Medium — device fingerprinting |
| **Timestamps** | DateTimeOriginal, CreateDate, ModifyDate | Medium — behavioral profiling |
| **User Comments** | UserComment, ImageDescription, XPComment, XPAuthor | **High** — may contain names, notes, PII |
| **Thumbnails** | ThumbnailImage (embedded JPEG preview) | **High** — may preserve original uncropped image |
| **Serial Numbers** | BodySerialNumber, LensSerialNumber, InternalSerialNumber | Medium — unique device tracking |
| **Network/Software** | HostComputer, Software, ProcessingSoftware | Low–Medium — infrastructure disclosure |
| **XMP / IPTC** | Creator, Rights, Description, Keywords | Medium — organizational/authorship leakage |

### Why This Matters in an ERP Context

ERP platforms are used by businesses with multiple employees, contractors, clients, and sometimes external partners accessing shared resources. The **Library** module is inherently a collaborative, shared-access feature. Any image uploaded by one party is downloadable by many others — creating a **one-to-many PII exposure vector**.

---

## Step-by-Step Reproduction

### Prerequisites

- A valid user account with access to the **Library** module (tested with Admin role; lower-privilege roles should also be tested)
- A test image file containing rich EXIF/metadata (see Step 1)
- An EXIF analysis tool: `exiftool` (CLI), or any online EXIF viewer

---

### Step 1: Prepare a Metadata-Rich Test Image

Create or obtain a JPEG image with embedded GPS and descriptive metadata. You can inject test metadata using `exiftool`:

```bash
exiftool \
  -GPSLatitude="48.8566" \
  -GPSLatitudeRef="N" \
  -GPSLongitude="2.3522" \
  -GPSLongitudeRef="E" \
  -GPSAltitude="35" \
  -UserComment="Confidential: Taken at employee home address" \
  -XPAuthor="John Doe" \
  -Make="Apple" \
  -Model="iPhone 15 Pro Max" \
  -DateTimeOriginal="2025:01:15 09:30:00" \
  test_image.jpg
```

Verify metadata is present:

```bash
exiftool test_image.jpg
```

Expected output should show all injected fields including GPS coordinates resolving to **Paris, France (48.8566°N, 2.3522°E)**.

---

### Step 2: Log in to Fectura Scripts

1. Navigate to the Fectura Scripts login page.
2. Authenticate with valid credentials.
3. Confirm access to the application dashboard.

---

### Step 3: Navigate to the Library Section

1. From the main navigation/sidebar, click on **"Library"** (or equivalent menu entry).
2. Confirm the Library module loads and displays existing files/images (if any).

---

### Step 4: Upload the Test Image

1. Click the **"Upload"** button/action within the Library interface.
2. Select the prepared `test_image.jpg` file.
3. Complete the upload process (fill any required fields such as title/description if prompted).
4. Confirm the image appears in the Library listing.

---

### Step 5: Download the Image (as the Same or Different User)

1. Locate the uploaded image in the Library.
2. Click the **"Download"** button/link (or right-click → Save As on the rendered image, depending on UI).
3. Save the file locally as `downloaded_image.jpg`.

> **Note:** For stronger proof of impact, perform this step logged in as a **different user account** with Library access, demonstrating cross-user information leakage.

---

### Step 6: Extract and Analyze Metadata from the Downloaded File

Run `exiftool` on the downloaded file:

```bash
exiftool downloaded_image.jpg
```

**Observed Result (Vulnerable):**

```
GPS Latitude                    : 48 deg 51' 23.76" N
GPS Longitude                   : 2 deg 21' 7.92" E
GPS Altitude                    : 35 m
GPS Position                    : 48.8566°N, 2.3522°E
User Comment                    : Confidential: Taken at employee home address
XP Author                       : John Doe
Make                            : Apple
Model                           : iPhone 15 Pro Max
Date/Time Original              : 2025:01:15 09:30:00
...
[ALL original metadata preserved in full]
```

**Expected Result (Secure):**

All EXIF, XMP, IPTC, GPS, and comment fields should be **stripped or neutralized** before storage or at download time. Only essential image rendering data should remain.

---

### Step 7: Confirm GPS Resolution to Physical Location

Take the extracted GPS coordinates and resolve them:

```
https://www.google.com/maps?q=48.8566,2.3522
```

This confirms the metadata resolves to a **precise, real-world physical location** — demonstrating the severity of the leak.

---

## Root Cause Analysis

The application's image upload handler in the Library module **stores the uploaded file byte-for-byte without any server-side processing to remove metadata**. The download handler then serves the identical file. At no point in the pipeline is any of the following performed:

1. **EXIF stripping** (e.g., via libraries like `Intervention Image`, `Imagick::stripImage()`, Python Pillow's `.save()` without EXIF, or `jpegtran -copy none`)
2. **Re-encoding / reprocessing** of the image (which would naturally discard non-image data)
3. **Selective metadata whitelisting** (preserving only color profile / orientation data)
4. **Content-Disposition header enforcement** to prevent inline rendering with metadata intact

This is a **design-level omission** rather than a bypassable control — there is simply no metadata handling logic present.

---

## Impact Assessment

### Direct Impacts

| Impact | Description | Severity |
|---|---|---|
| **Geolocation Disclosure** | GPS coordinates in uploaded photos can reveal home addresses, office locations, client sites, travel patterns of employees | **High** |
| **PII Leakage** | Author names, comments, device owner names embedded in metadata expose personal identity | **High** |
| **Device Fingerprinting** | Camera make/model, serial numbers, and software versions enable tracking and targeting of specific individuals or devices | **Medium** |
| **Behavioral Profiling** | Timestamps and sequential GPS data across multiple uploads can reconstruct an individual's movements and schedule | **High** |
| **Embedded Thumbnail Leakage** | Thumbnails may preserve the original uncropped image, potentially exposing content the user intentionally cropped out (documented in prior CVEs) | **Medium–High** |

### Contextual / Escalated Impacts

- **Regulatory Exposure:** GPS coordinates and author names constitute **personal data** under GDPR (Art. 4(1)), CCPA, and similar frameworks. Failure to strip this data from shared/downloadable resources may constitute a **data protection violation** for organizations using Fectura Scripts.
- **Insider Threat Amplification:** A malicious insider (employee, contractor) with Library download access can silently harvest geolocation and identity data of colleagues without any logging or indication to the victim.
- **Physical Security Risk:** In sectors where employee physical safety is paramount (e.g., legal, law enforcement, journalism, NGOs, domestic violence support), leaking home GPS coordinates through an ERP system represents a **direct physical safety threat**.
- **Supply Chain Risk:** If the Library is shared with external partners/vendors, the exposure surface extends beyond the organization.

### Why CVSS 6.5 Understates the Risk

The CVSS base score of 6.5 reflects the mechanical characteristics of the vulnerability (network-accessible, low complexity, authenticated). However, the **contextual severity is higher** because:

1. Users have **no expectation** that uploading an image to an ERP system will broadcast their home coordinates.
2. The attack is **completely passive** — the attacker simply downloads a file; no exploitation toolkit or special skills are required.
3. The leaked data (GPS, PII) is **irrevocable** — once downloaded, the victim cannot "un-leak" their location.
4. The vulnerability affects **every image ever uploaded** to the Library, creating a retroactive exposure of historical data.

**Recommended effective severity: HIGH for any deployment handling real employee/client data.**

---

## Recommended Remediation

### Immediate (Short-Term)

| Priority | Action |
|---|---|
| **P0** | Implement **server-side EXIF/metadata stripping** on all image uploads in the Library module **before storage**. |
| **P0** | **Retroactively strip metadata** from all existing images already stored in the Library. |
| **P1** | Extend metadata stripping to **all other upload endpoints** across the application (email attachments, profile photos, product images, etc.). |

### Implementation Guidance (by Language/Stack)

**PHP (likely stack for Fectura Scripts):**

```php
// Using GD (built-in, no dependencies)
function stripMetadata($sourcePath, $destPath) {
    $image = imagecreatefromjpeg($sourcePath);
    imagejpeg($image, $destPath, 95); // Re-encodes, discarding all EXIF
    imagedestroy($image);
}

// Using Imagick (if available)
$img = new Imagick($sourcePath);
$img->stripImage(); // Removes all EXIF, IPTC, XMP profiles
$img->writeImage($destPath);
```

**Python:**

```python
from PIL import Image
img = Image.open("uploaded.jpg")
data = list(img.getdata())
clean = Image.new(img.mode, img.size)
clean.putdata(data)
clean.save("clean.jpg")
```

**Command-line (for retroactive cleanup):**

```bash
# Strip all metadata from all JPEGs in the library storage directory
exiftool -all= -overwrite_original /path/to/library/uploads/*.jpg
```

### Long-Term (Architectural)

| Priority | Action |
|---|---|
| **P1** | Establish a **centralized file upload processing pipeline** that all modules route through, ensuring consistent sanitization. |
| **P1** | Add **Content Security Policy** and `Content-Disposition: attachment` headers on all file downloads to reduce inline rendering risks. |
| **P2** | Implement a configurable **metadata policy** (e.g., allow admins to choose between full strip, preserve orientation only, or preserve color profile). |
| **P2** | Add **file type validation** (magic byte checking, not just extension) to the upload pipeline. |
| **P3** | Consider adding a **user-facing warning** at upload time: "Note: Image metadata will be stripped for privacy." |

---

## 9. References

| Resource | URL |
|---|---|
| CWE-200: Exposure of Sensitive Information | https://cwe.mitre.org/data/definitions/200.html |
| CWE-212: Improper Removal of Sensitive Information Before Storage or Transfer | https://cwe.mitre.org/data/definitions/212.html |
| NIST NVD CVSS v3.1 Calculator | https://www.first.org/cvss/calculator/3.1 |
| GDPR Art. 4(1) — Definition of Personal Data | https://gdpr-info.eu/art-4-gdpr/ |
| ExifTool by Phil Harvey | https://exiftool.org/ |
| Related CVE | https://nvd.nist.gov/vuln/detail/CVE-2023-29850 |
---

## 11. Conclusion

The absence of image metadata sanitization in Fectura Scripts' Library module is a **clear, easily exploitable, and high-impact information disclosure vulnerability**. It requires no technical skill to exploit (just a file download and a free tool), it leaks data that users never intended to share (home GPS coordinates, personal identity), and it affects every image ever uploaded to the platform retroactively.

While the CVSS base score of **6.5** categorizes this as "Medium," the real-world privacy consequences — particularly under GDPR and in contexts where physical safety is relevant — warrant treating this with **High urgency**. The fix is straightforward, well-documented, and should be implemented immediately across all upload endpoints.


<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/80cbdd80-fc80-45f2-b125-e0557e94ac40" />

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/53fd80bb-cd41-48d6-a9b8-3129f307bce6" />

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-q7f2-rv22-2xgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27892
- https://github.com/NeoRazorX/facturascripts/commit/b0725147a61a9a377b7180589af33ff52b4751e2
- https://github.com/NeoRazorX/facturascripts
