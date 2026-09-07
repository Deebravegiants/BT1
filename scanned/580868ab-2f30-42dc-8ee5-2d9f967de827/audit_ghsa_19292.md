# [M] Mobile Security Framework (MobSF) Allows Stored Cross Site Scripting (XSS) via malicious SVG Icon Upload

## Summary
Severity: Medium
Advisory: GHSA-mwfg-948f-2cc5
CVE: CVE-2025-46335
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-mwfg-948f-2cc5
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.3.3

## Details
**Vulnerable MobSF Versions:**  <= v4.3.2

**CVSS V4.0 Score:** 8.6 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)

**Details:**
A Stored Cross-Site Scripting (XSS) vulnerability has been identified in MobSF versions ≤ 4.3.2. The vulnerability arises from improper sanitization of user-supplied SVG files during the Android APK analysis workflow.

When an Android Studio project contains a malicious SVG file as an app icon (e.g path, /app/src/main/res/mipmap-hdpi/ic_launcher.svg), and the project is zipped and uploaded to MobSF, the tool processes and extracts the contents without validating or sanitizing the SVG. 

Upcon ZIP extraction this icon file is saved by MobSF to: user/.MobSF/downloads/<filename>.svg

This file becomes publicly accessible via the web interface at:

http://127.0.0.1:8081/download/filename.svg

If the SVG contains embedded JavaScript (e.g., an XSS payload), accessing this URL via a browser leads to the execution of the script in the context of the MobSF user session, resulting in stored XSS.

**Proof Of Concept:**

1. Create a malicious SVG file (ic_launcher.svg) with an embedded XSS payload.

![01](https://github.com/user-attachments/assets/9a89dec2-0671-490d-aba6-f38470bd84ee)

2. Place the file in the Android Studio project directory: /app/src/main/res/mipmap-hdpi/ic_launcher.svg

![02](https://github.com/user-attachments/assets/fc66f659-9f90-4be8-92c3-c5f26e1e11de)

3. Zip the project directory and upload it to MobSF.

![03](https://github.com/user-attachments/assets/a8465037-3b7a-42b7-89cf-5102c27917e7)

4. After the scan, navigate to the "Recent Scans" page in the MobSF web interface and click on the scan entry and open the icon file in a new browser tab.

![04](https://github.com/user-attachments/assets/5355e4d3-89a2-403a-a1a7-f60389fdbb8d)

5. The XSS payload is executed, confirming the vulnerability.

![05](https://github.com/user-attachments/assets/bc1e3493-1ffc-4598-b122-85459a406748)

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-mwfg-948f-2cc5
- https://nvd.nist.gov/vuln/detail/CVE-2025-46335
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/6987a946485a795f4fd38cebdb4860b368a1995d
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
