# [M] CVE-2020-15693

## Summary
Severity: Medium
Advisory: CVE-2020-15693
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-08-14
Source: https://osv.dev/vulnerability/CVE-2020-15693
Type: osv

## Details
In Nim 1.2.4, the standard library httpClient is vulnerable to a CR-LF injection in the target URL. An injection is possible if the attacker controls any part of the URL provided in a call (such as httpClient.get or httpClient.post), the User-Agent header value, or custom HTTP header names or values.

## References
- https://nim-lang.org/blog/2020/07/30/versions-126-and-108-released.html
- https://github.com/nim-lang/Nim/blob/dc5a40f3f39c6ea672e6dc6aca7f8118a69dda99/lib/pure/httpclient.nim#L1023
- http://www.openwall.com/lists/oss-security/2021/02/04/2
- https://consensys.net/diligence/vulnerabilities/nim-httpclient-header-crlf-injection/
