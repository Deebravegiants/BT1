# [C] CVE-2022-3890

## Summary
Severity: Critical
Advisory: CVE-2022-3890
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-11-09
Source: https://osv.dev/vulnerability/CVE-2022-3890
Type: osv

## Details
Heap buffer overflow in Crashpad in Google Chrome on Android prior to 107.0.5304.106 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: High)

## References
- https://chromereleases.googleblog.com/2022/11/stable-channel-update-for-desktop.html
- https://www.debian.org/security/2022/dsa-5275
- https://crbug.com/1380083
