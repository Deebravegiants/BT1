# [H] CVE-2022-0453

## Summary
Severity: High
Advisory: CVE-2022-0453
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-0453
Type: osv

## Details
Use after free in Reader Mode in Google Chrome prior to 98.0.4758.80 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2022/02/stable-channel-update-for-desktop.html
- https://crbug.com/1284916
