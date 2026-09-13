# [M] CVE-2018-20450

## Summary
Severity: Medium
Advisory: CVE-2018-20450
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20450
Type: osv

## Details
The read_MSAT function in ole.c in libxls 1.4.0 has a double free that allows attackers to cause a denial of service (application crash) via a crafted file, a different vulnerability than CVE-2017-2897.

## References
- https://security.gentoo.org/glsa/202003-64
- https://github.com/evanmiller/libxls/issues/34
