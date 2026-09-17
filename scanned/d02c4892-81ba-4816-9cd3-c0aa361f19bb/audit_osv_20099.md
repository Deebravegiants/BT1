# [H] CVE-2021-30463

## Summary
Severity: High
Advisory: CVE-2021-30463
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-30463
Type: osv

## Details
VestaCP through 0.9.8-24 allows attackers to gain privileges by creating symlinks to files for which they lack permissions. After reading the RKEY value from user.conf under the /usr/local/vesta/data/users/admin directory, the admin password can be changed via a /reset/?action=confirm&user=admin&code= URI. This occurs because chmod is used unsafely.

## References
- https://ssd-disclosure.com/ssd-advisory-vestacp-lpe-vulnerabilities/
