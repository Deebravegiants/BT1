# [M] aiohttp's ClientSession is vulnerable to CRLF injection via version

## Summary
Severity: Medium
Advisory: GHSA-q3qx-c6g2-7pw2
CVE: CVE-2023-49081
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-q3qx-c6g2-7pw2
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.9.0

## Details
### Summary
Improper validation make it possible for an attacker to modify the HTTP request (e.g. to insert a new header) or even create a new HTTP request if the attacker controls the HTTP version.

### Details
The vulnerability only occurs if the attacker can control the HTTP version of the request (including its type).
For example if an unvalidated JSON value is used as a version and the attacker is then able to pass an array as the `version` parameter.
Furthermore, the vulnerability only occurs when the `Connection` header is passed to the `headers` parameter.

At this point, the library will use the parsed value to create the request. If a list is passed, then it bypasses validation and it is possible to perform CRLF injection.

### PoC
The POC below shows an example of providing an unvalidated array as a version:
https://gist.github.com/jnovikov/184afb593d9c2114d77f508e0ccd508e

### Impact
CRLF injection leading to Request Smuggling.

### Workaround
If these specific conditions are met and you are unable to upgrade, then validate the user input to the `version` parameter to ensure it is a `str`.

Patch: https://github.com/aio-libs/aiohttp/pull/7835/files

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-q3qx-c6g2-7pw2
- https://nvd.nist.gov/vuln/detail/CVE-2023-49081
- https://github.com/aio-libs/aiohttp/pull/7835/files
- https://github.com/aio-libs/aiohttp/commit/1e86b777e61cf4eefc7d92fa57fa19dcc676013b
- https://gist.github.com/jnovikov/184afb593d9c2114d77f508e0ccd508e
- https://github.com/aio-libs/aiohttp
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp/PYSEC-2023-250.yaml
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TY5SI6NK5243DEEDQUFKQKW5GQNKQUMA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WSYWMP64ZFCTC3VO6RY6EC6VSSMV6I3A
