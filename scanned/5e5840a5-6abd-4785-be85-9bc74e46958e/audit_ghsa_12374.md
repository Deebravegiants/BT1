# [M] Unbounded queuing of path validation messages in cloudflare-quiche

## Summary
Severity: Medium
Advisory: GHSA-w3vp-jw9m-f9pm
CVE: CVE-2023-6193
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-w3vp-jw9m-f9pm
Type: github-advisory

## Affected
- crates.io: `quiche` — affected >=0.15.0 <0.19.1

## Details
### Impact
quiche v. 0.15.0 through 0.19.0 was discovered to be vulnerable to unbounded queuing of path validation messages, which could lead to excessive resource consumption.

QUIC path validation ([RFC 9000 Section 8.2](https://datatracker.ietf.org/doc/html/rfc9000#section-8.2)) requires that the recipient of a PATH_CHALLENGE frame responds by sending a PATH_RESPONSE. An unauthenticated remote attacker can exploit the vulnerability by sending PATH_CHALLENGE frames and manipulating the connection (e.g. by restricting the peer's congestion window size) so that PATH_RESPONSE frames can only be sent at the slower rate than they are received, leading to storage of path validation data in an unbounded queue.

### Patches
Quiche versions greater than 0.19.0 address this problem.

### References
[CVE-2023-6193](https://www.cve.org/CVERecord?id=CVE-2023-6193)
[RFC 9000 Section 8.2](https://datatracker.ietf.org/doc/html/rfc9000#section-8.2)

## References
- https://github.com/cloudflare/quiche/security/advisories/GHSA-w3vp-jw9m-f9pm
- https://nvd.nist.gov/vuln/detail/CVE-2023-6193
- https://github.com/cloudflare/quiche/commit/ea7ecf39ae28ab24cf1785c1674dc2e8a076f9ca
- https://datatracker.ietf.org/doc/html/rfc9000#section-8.2
- https://github.com/cloudflare/quiche
