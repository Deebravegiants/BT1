# [H] CVE-2017-6319

## Summary
Severity: High
Advisory: CVE-2017-6319
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6319
Type: osv

## Details
The dex_parse_debug_item function in libr/bin/p/bin_dex.c in radare2 1.2.1 allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted DEX file.

## References
- http://www.securityfocus.com/bid/96520
- https://github.com/radare/radare2/commit/ad55822430a03fe075221b543efb434567e9e431
- https://github.com/radare/radare2/issues/6836
