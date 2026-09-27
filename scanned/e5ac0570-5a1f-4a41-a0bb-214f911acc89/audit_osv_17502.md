# [H] CVE-2020-15694

## Summary
Severity: High
Advisory: CVE-2020-15694
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-08-14
Source: https://osv.dev/vulnerability/CVE-2020-15694
Type: osv

## Details
In Nim 1.2.4, the standard library httpClient fails to properly validate the server response. For example, httpClient.get().contentLength() does not raise any error if a malicious server provides a negative Content-Length.

## References
- https://nim-lang.org/blog/2020/07/30/versions-126-and-108-released.html
- https://github.com/nim-lang/Nim/blob/dc5a40f3f39c6ea672e6dc6aca7f8118a69dda99/lib/pure/httpclient.nim#L241
- http://www.openwall.com/lists/oss-security/2021/02/04/2
- https://consensys.net/diligence/vulnerabilities/nim-httpclient-header-crlf-injection/
