# [H] CVE-2016-7544

## Summary
Severity: High
Advisory: CVE-2016-7544
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-7544
Type: osv

## Details
Crypto++ 5.6.4 incorrectly uses Microsoft's stack-based _malloca and _freea functions. The library will request a block of memory to align a table in memory. If the table is later reallocated, then the wrong pointer could be freed.

## References
- http://www.securityfocus.com/bid/93164
- https://www.cryptopp.com/release565.html
- http://www.openwall.com/lists/oss-security/2016/09/23/5
- http://www.openwall.com/lists/oss-security/2016/09/23/9
- https://github.com/weidai11/cryptopp/issues/302
