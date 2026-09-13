# [H] CVE-2023-4366

## Summary
Severity: High
Advisory: CVE-2023-4366
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-15
Source: https://osv.dev/vulnerability/CVE-2023-4366
Type: osv

## Details
Use after free in Extensions in Google Chrome prior to 116.0.5845.96 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: Medium)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DMXHPRUGBUDNHZCZCIVMWAUIEXEGMGT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OCFEK63FUHFXZH5MSG6TNQOXMQWM4M5S/
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5479
- https://chromereleases.googleblog.com/2023/08/stable-channel-update-for-desktop_15.html
- https://crbug.com/1450784
