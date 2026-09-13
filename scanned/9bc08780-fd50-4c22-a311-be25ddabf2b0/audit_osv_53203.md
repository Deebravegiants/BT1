# [M] CVE-2022-3314

## Summary
Severity: Medium
Advisory: CVE-2022-3314
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-3314
Type: osv

## Details
Use after free in logging in Google Chrome prior to 106.0.5249.62 allowed a remote attacker who had compromised a WebUI process to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: Medium)

## References
- https://chromereleases.googleblog.com/2022/09/stable-channel-update-for-desktop_27.html
- https://crbug.com/1328708
