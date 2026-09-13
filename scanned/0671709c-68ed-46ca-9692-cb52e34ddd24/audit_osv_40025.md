# [H] PHP Standard Library: HTTP/2 server-side missing content-length validation enables request smuggling

## Summary
Severity: High
Advisory: CVE-2026-48979
Aliases: GHSA-pw9p-jvrm-f7rm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-48979
Type: osv

## Details
PHP Standard Library (PSL) is set of APIs covering async, collections, networking, I/O, cryptography, terminal UI, etc. In versions 6.1.0, 6.1.1 and 6.2.0, the Psl\H2\ServerConnection does not validate that the total bytes received in DATA frames match the content-length header declared in the HEADERS frame, allowing request smuggling. This is in violation of RFC 9113 §8.1.1. A malicious client is able to send more DATA bytes than declared, smuggling additional content past application-level size limits and send fewer DATA bytes than declared and close the stream early, causing applications that trust the declared length to behave incorrectly.
The vulnerability is only reachable for consumers using Psl\H2\ServerConnection directly to accept untrusted client traffic. Consumers of documented high-level PSL APIs are not affected. This issue has been fixed in versions 6.1.2 and 6.2.1.

## References
- https://github.com/php-standard-library/php-standard-library/releases/tag/6.1.2
- https://github.com/php-standard-library/php-standard-library/releases/tag/6.2.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48979.json
- https://github.com/php-standard-library/php-standard-library/security/advisories/GHSA-pw9p-jvrm-f7rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-48979
