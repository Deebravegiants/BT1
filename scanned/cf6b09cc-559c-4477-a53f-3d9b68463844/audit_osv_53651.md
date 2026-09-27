# [M] CVE-2023-1217

## Summary
Severity: Medium
Advisory: CVE-2023-1217
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/CVE-2023-1217
Type: osv

## Details
Stack buffer overflow in Crash reporting in Google Chrome on Windows prior to 111.0.5563.64 allowed a remote attacker who had compromised the renderer process to obtain potentially sensitive information from process memory via a crafted HTML page. (Chromium security severity: High)

## References
- https://chromereleases.googleblog.com/2023/03/stable-channel-update-for-desktop.html
- https://crbug.com/1412658
