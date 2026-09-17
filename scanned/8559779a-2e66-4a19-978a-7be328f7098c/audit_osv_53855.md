# [H] CVE-2023-2930

## Summary
Severity: High
Advisory: CVE-2023-2930
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-2930
Type: osv

## Details
Use after free in Extensions in Google Chrome prior to 114.0.5735.90 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- https://chromereleases.googleblog.com/2023/05/stable-channel-update-for-desktop_30.html
- https://security.gentoo.org/glsa/202311-11
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5418
- https://crbug.com/1443401
