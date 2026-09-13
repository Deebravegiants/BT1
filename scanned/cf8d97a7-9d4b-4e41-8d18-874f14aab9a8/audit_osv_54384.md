# [M] CVE-2023-5473

## Summary
Severity: Medium
Advisory: CVE-2023-5473
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-10-11
Source: https://osv.dev/vulnerability/CVE-2023-5473
Type: osv

## Details
Use after free in Cast in Google Chrome prior to 118.0.5993.70 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: Low)

## References
- https://chromereleases.googleblog.com/2023/10/stable-channel-update-for-desktop_10.html
- https://security.gentoo.org/glsa/202311-11
- https://security.gentoo.org/glsa/202312-07
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5526
- https://crbug.com/1484000
