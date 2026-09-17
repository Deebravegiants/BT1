# [H] CVE-2017-6362

## Summary
Severity: High
Advisory: CVE-2017-6362
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-07
Source: https://osv.dev/vulnerability/CVE-2017-6362
Type: osv

## Details
Double free vulnerability in the gdImagePngPtr function in libgd2 before 2.2.5 allows remote attackers to cause a denial of service via vectors related to a palette with no colors.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N2BLXX7KNRE7ZVQAKGTHHWS33CUCXVUP/
- http://www.debian.org/security/2017/dsa-3961
- https://github.com/libgd/libgd/issues/381
- https://github.com/libgd/libgd/releases/tag/gd-2.2.5
