# [H] CVE-2023-3422

## Summary
Severity: High
Advisory: CVE-2023-3422
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-26
Source: https://osv.dev/vulnerability/CVE-2023-3422
Type: osv

## Details
Use after free in Guest View in Google Chrome prior to 114.0.5735.198 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KREKCQTJDVI2AEBG5ECZPSOQXIC2L5XL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBAHED5YFJPRGSEKNZIYHZBGSVHGEHOH/
- https://chromereleases.googleblog.com/2023/06/stable-channel-update-for-desktop_26.html
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5440
- https://crbug.com/1450397
