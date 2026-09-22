# [H] CVE-2022-0302

## Summary
Severity: High
Advisory: CVE-2022-0302
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-12
Source: https://osv.dev/vulnerability/CVE-2022-0302
Type: osv

## Details
Use after free in Omnibox in Google Chrome prior to 97.0.4692.99 allowed an attacker who convinced a user to engage in specific user interactions to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2022/01/stable-channel-update-for-desktop_19.html
- https://crbug.com/1278613
