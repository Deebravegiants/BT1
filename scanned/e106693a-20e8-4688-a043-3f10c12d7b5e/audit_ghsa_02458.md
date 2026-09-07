# [M] HTTP Request smuggling in tiny_http

## Summary
Severity: Medium
Advisory: GHSA-7v2r-wxmg-mgvc
CVE: CVE-2020-35884
CWE: CWE-444
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7v2r-wxmg-mgvc
Type: github-advisory

## Affected
- crates.io: `tiny_http` — affected >=0 <0.8.0

## Details
HTTP pipelining issues and request smuggling attacks are possible due to incorrect Transfer encoding header parsing. It is possible conduct HTTP request smuggling attacks (CL:TE/TE:TE) by sending invalid Transfer Encoding headers. By manipulating the HTTP response the attacker could poison a web-cache, perform an XSS attack, or obtain sensitive information from requests other than their own.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35884
- https://github.com/tiny-http/tiny-http/issues/173
- https://github.com/tiny-http/tiny-http/pull/190
- https://github.com/tiny-http/tiny-http/commit/623b87397a569729c4bcabae747823c5668cce94
- https://github.com/tiny-http/tiny-http
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/M3JDNRE5RXJOWZZZF5QSCG4GUCSLTHF2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VO6SRTCEPEYO2OX647I3H5XUWLFDRDWL
- https://rustsec.org/advisories/RUSTSEC-2020-0031.html
