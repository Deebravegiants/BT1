# [H] android-gif-drawable Double Free vulnerability

## Summary
Severity: High
Advisory: GHSA-x534-j49x-mqvj
CVE: CVE-2019-11932
CWE: CWE-415
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x534-j49x-mqvj
Type: github-advisory

## Affected
- Maven: `pl.droidsonroids.gif:android-gif-drawable` — affected >=0 <1.2.18

## Details
A double free vulnerability in the DDGifSlurp function in decoding.c in the android-gif-drawable library before version 1.2.18, as used in WhatsApp for Android before version 2.19.244 and many other Android applications, allows remote attackers to execute arbitrary code or cause a denial of service when the library is used to parse a specially crafted GIF image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11932
- https://github.com/koral--/android-gif-drawable/pull/673
- https://github.com/koral--/android-gif-drawable/pull/673/commits/4944c92761e0a14f04868cbcf4f4e86fd4b7a4a9
- https://github.com/koral--/android-gif-drawable/commit/cc5b4f8e43463995a84efd594f89a21f906c2d20
- https://awakened1712.github.io/hacking/hacking-whatsapp-gif-rce
- https://gist.github.com/wdormann/874198c1bd29c7dd2157d9fc1d858263
- https://github.com/koral--/android-gif-drawable
- https://www.facebook.com/security/advisories/cve-2019-11932
- http://packetstormsecurity.com/files/154867/Whatsapp-2.19.216-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/158306/WhatsApp-android-gif-drawable-Double-Free.html
- http://seclists.org/fulldisclosure/2019/Nov/27
