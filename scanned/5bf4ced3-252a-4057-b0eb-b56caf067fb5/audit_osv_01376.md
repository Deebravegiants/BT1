# [C] ALPINE-CVE-2019-12525

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-12525
Ecosystem: Alpine:v3.10, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12525
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=3.3.9 <4.8-r0
- Alpine:v3.9: `squid` — affected >=3.3.9 <4.8-r0

## Details
An issue was discovered in Squid 3.3.9 through 3.5.28 and 4.x through 4.7. When Squid is configured to use Digest authentication, it parses the header Proxy-Authorization. It searches for certain tokens such as domain, uri, and qop. Squid checks if this token's value starts with a quote and ends with one. If so, it performs a memcpy of its length minus 2. Squid never checks whether the value is just a single quote (which would satisfy its requirements), leading to a memcpy of its length minus 1.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12525
