# [C] CVE-2020-16024

## Summary
Severity: Critical
Advisory: CVE-2020-16024
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2020-16024
Type: osv

## Details
Heap buffer overflow in UI in Google Chrome prior to 87.0.4280.66 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- http://packetstormsecurity.com/files/161353/Chrome-SkBitmapOperations-UnPreMultiply-Heap-Buffer-Overflow.html
- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop_17.html
- https://crbug.com/1147430
