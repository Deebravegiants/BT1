# [M] CVE-2018-8050

## Summary
Severity: Medium
Advisory: CVE-2018-8050
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-11
Source: https://osv.dev/vulnerability/CVE-2018-8050
Type: osv

## Details
The af_get_page() function in lib/afflib_pages.cpp in AFFLIB (aka AFFLIBv3) through 3.7.16 allows remote attackers to cause a denial of service (segmentation fault) via a corrupt AFF image that triggers an unexpected pagesize value.

## References
- https://github.com/sshock/AFFLIBv3/commit/435a2ca802358a3debb6d164d2c33049131df81c
