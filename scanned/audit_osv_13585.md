# [H] CVE-2018-20452

## Summary
Severity: High
Advisory: CVE-2018-20452
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20452
Type: osv

## Details
The read_MSAT_body function in ole.c in libxls 1.4.0 has an invalid free that allows attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted file, because of inconsistent memory management (new versus free) in ole2_read_header in ole.c.

## References
- https://security.gentoo.org/glsa/202003-64
- https://github.com/evanmiller/libxls/issues/35
