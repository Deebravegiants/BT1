# [H] CVE-2023-0135

## Summary
Severity: High
Advisory: CVE-2023-0135
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-01-10
Source: https://osv.dev/vulnerability/CVE-2023-0135
Type: osv

## Details
Use after free in Cart in Google Chrome prior to 109.0.5414.74 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via database corruption and a crafted HTML page. (Chromium security severity: Medium)

## References
- https://chromereleases.googleblog.com/2023/01/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202305-10
- https://security.gentoo.org/glsa/202311-11
- https://crbug.com/1385831
