# [H] CVE-2022-2477

## Summary
Severity: High
Advisory: CVE-2022-2477
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-07-28
Source: https://osv.dev/vulnerability/CVE-2022-2477
Type: osv

## Details
Use after free in Guest View in Google Chrome prior to 103.0.5060.134 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YKLJ3B3D5BCVWE3QNP4N7HHF26OHD567/
- https://chromereleases.googleblog.com/2022/07/stable-channel-update-for-desktop_19.html
- https://security.gentoo.org/glsa/202208-35
- https://crbug.com/1336266
