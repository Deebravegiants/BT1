# [H] CVE-2022-0605

## Summary
Severity: High
Advisory: CVE-2022-0605
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-0605
Type: osv

## Details
Use after free in Webstore API in Google Chrome prior to 98.0.4758.102 allowed an attacker who convinced a user to install a malicious extension and convinced a user to enage in specific user interaction to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2022/02/stable-channel-update-for-desktop_14.html
- https://crbug.com/1286940
