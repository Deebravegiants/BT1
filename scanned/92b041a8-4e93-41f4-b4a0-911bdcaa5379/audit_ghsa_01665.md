# [M] HTTP Response Splitting in Puma

## Summary
Severity: Medium
Advisory: GHSA-84j7-475p-hp8v
CVE: CVE-2020-5247
CWE: CWE-113
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2020-02-28
Source: https://github.com/advisories/GHSA-84j7-475p-hp8v
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=0 <3.12.4
- RubyGems: `puma` — affected >=4.0.0 <4.3.3

## Details
In Puma (RubyGem) before 4.3.2 and 3.12.3, if an application using Puma allows untrusted input in a response header, an attacker can use newline characters (i.e. `CR`, `LF` or`/r`, `/n`) to end the header and inject malicious content, such as additional headers or an entirely new response body. This vulnerability is known as HTTP Response Splitting.

While not an attack in itself, response splitting is a vector for several other attacks, such as cross-site scripting (XSS).

This is related to CVE-2019-16254, which fixed this vulnerability for the WEBrick Ruby web server.

This has been fixed in versions 4.3.2 and 3.12.3 by checking all headers for line endings and rejecting headers with those characters.

## References
- https://github.com/puma/puma/security/advisories/GHSA-84j7-475p-hp8v
- https://nvd.nist.gov/vuln/detail/CVE-2020-5247
- https://github.com/puma/puma/commit/c36491756f68a9d6a8b3a49e7e5eb07fe6f1332f
- https://github.com/puma/puma
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2020-5247.yml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BMJ3CGZ3DLBJ5WUUKMI5ZFXFJQMXJZIK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DIHVO3CQMU7BZC7FCTSRJ33YDNS3GFPK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NJ3LL5F5QADB6LM46GXZETREAKZMQNRD
- https://owasp.org/www-community/attacks/HTTP_Response_Splitting
- https://www.ruby-lang.org/en/news/2019/10/01/http-response-splitting-in-webrick-cve-2019-16254
