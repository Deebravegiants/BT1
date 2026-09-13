# [M] CVE-2017-6387

## Summary
Severity: Medium
Advisory: CVE-2017-6387
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6387
Type: osv

## Details
The dex_loadcode function in libr/bin/p/bin_dex.c in radare2 1.2.1 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted DEX file.

## References
- http://www.securityfocus.com/bid/96521
- https://github.com/radare/radare2/commit/ead645853a63bf83d8386702cad0cf23b31d7eeb
- https://github.com/radare/radare2/issues/6857
