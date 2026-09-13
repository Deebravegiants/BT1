# [H] CVE-2023-1220

## Summary
Severity: High
Advisory: CVE-2023-1220
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/CVE-2023-1220
Type: osv

## Details
Heap buffer overflow in UMA in Google Chrome prior to 111.0.5563.64 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- http://packetstormsecurity.com/files/171796/Chrome-base-SampleVectorBase-MoveSingleSampleToCounts-Heap-Buffer-Overflow.html
- https://chromereleases.googleblog.com/2023/03/stable-channel-update-for-desktop.html
- https://crbug.com/1417185
