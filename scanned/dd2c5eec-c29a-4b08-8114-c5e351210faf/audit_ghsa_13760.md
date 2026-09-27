# [M] aiohttp's ClientSession is vulnerable to CRLF injection via method

## Summary
Severity: Medium
Advisory: GHSA-qvrw-v9rv-5rjx
CVE: CVE-2023-49082
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-qvrw-v9rv-5rjx
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.9.0

## Details
### Summary
Improper validation makes it possible for an attacker to modify the HTTP request (e.g. insert a new header) or even create a new HTTP request if the attacker controls the HTTP method.

### Details
The vulnerability occurs only if the attacker can control the HTTP method (GET, POST etc.) of the request.

Previous releases performed no validation on the provided value. If an attacker controls the HTTP method it will be used as is and can lead to HTTP request smuggling.

### PoC
A minimal example can be found here:
https://gist.github.com/jnovikov/7f411ae9fe6a9a7804cf162a3bdbb44b

### Impact
If the attacker can control the HTTP version of the request it will be able to modify the request (request smuggling).

### Workaround
If unable to upgrade and using user-provided values for the request method, perform manual validation of the user value (e.g. by restricting it to a few known values like GET, POST etc.).

Patch: https://github.com/aio-libs/aiohttp/pull/7806/files

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-qvrw-v9rv-5rjx
- https://nvd.nist.gov/vuln/detail/CVE-2023-49082
- https://github.com/aio-libs/aiohttp/pull/7806/files
- https://github.com/aio-libs/aiohttp/commit/e4ae01c2077d2cfa116aa82e4ff6866857f7c466
- https://gist.github.com/jnovikov/7f411ae9fe6a9a7804cf162a3bdbb44b
- https://github.com/aio-libs/aiohttp
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp/PYSEC-2023-251.yaml
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TY5SI6NK5243DEEDQUFKQKW5GQNKQUMA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WSYWMP64ZFCTC3VO6RY6EC6VSSMV6I3A
