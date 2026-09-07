# [M] NocoDB: Server-Side Request Forgery via Database Connection Host

## Summary
Severity: Medium
Advisory: GHSA-w43h-r5m5-p832
CVE: CVE-2026-47382
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-w43h-r5m5-p832
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
The connection-test endpoint opened a raw TCP socket to the user-supplied database
host without resolving and range-checking the destination, so private and link-local
addresses (including IPv4-mapped IPv6 forms and `localhost`) reached the driver.

### Details
A new `validateDbConnectionHost` helper resolves hostnames through DNS, parses each
address with `ipaddr.js`, normalises IPv4-mapped IPv6, and rejects addresses in the
private, loopback, link-local, unique-local, reserved, unspecified, broadcast, and
carrier-grade-NAT ranges. `0.0.0.0`, `::`, and the literal `localhost` are special-cased.
The check runs before the existing SSL block in the connection-test controller and
gates the driver invocation.

### Impact
Authenticated users with connection-test permission could probe internal services
(Redis, the cloud metadata endpoint, internal databases) reachable from the NocoDB
process. A DNS rebinding attacker could still race the resolve-vs-connect window.

### Credit
This issue was reported by [@helwor-01](https://github.com/helwor-01).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-w43h-r5m5-p832
- https://nvd.nist.gov/vuln/detail/CVE-2026-47382
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
