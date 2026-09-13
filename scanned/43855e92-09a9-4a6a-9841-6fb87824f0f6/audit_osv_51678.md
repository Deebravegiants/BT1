# [C] CVE-2021-37981

## Summary
Severity: Critical
Advisory: CVE-2021-37981
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-11-02
Source: https://osv.dev/vulnerability/CVE-2021-37981
Type: osv

## Details
Heap buffer overflow in Skia in Google Chrome prior to 95.0.4638.54 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2021/10/stable-channel-update-for-desktop_19.html
- https://www.debian.org/security/2022/dsa-5046
- https://crbug.com/1246631
