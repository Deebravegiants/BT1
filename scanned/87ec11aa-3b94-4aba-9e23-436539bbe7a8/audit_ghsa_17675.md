# [M] letmein connection limiter allows an arbitrary amount of simultaneous connections

## Summary
Severity: Medium
Advisory: GHSA-jpv7-p47h-f43j
CVE: CVE-2025-52570
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-06-23
Source: https://github.com/advisories/GHSA-jpv7-p47h-f43j
Type: github-advisory

## Affected
- crates.io: `letmeind` — affected >=0 <10.2.1
- crates.io: `letmeinfwd` — affected >=0 <10.2.1

## Details
### Impact

The connection limiter is implemented incorrectly.
It allows an arbitrary amount of simultaneously incoming connections (TCP, UDP and Unix socket) for the services `letmeind` and `letmeinfwd`.
Therefore, the command line option `num-connections` is not effective and does not limit the number of simultaneously incoming connections.

`letmeind` is the public network facing daemon (TCP/UDP).

`letmeinfwd` is the internal firewall daemon that only listens on local Unix socket.

Possible Denial Of Service by resource exhaustion.

### Affected versions
All versions `<= 10.2.0` are affected.

### Patches
All users shall upgrade to version `10.2.1`.

### Workarounds

Untested possible workarounds:
- It might be possible to limit the number of active connections to the `letmeind` port (default 5800) via firewall.
- The resource consumption of the service might be restricted with a service manager such as systemd.

### Severity:

If a (D)DoS is run against the service, *something* is going to be affected.
The connection limiter assures that the effect on the system itself is limited at the expense of the effect on the letmein services itself.
So even with the connection limiter active, a (D)DoS can lead to a less responsive or unresponsive letmein service.

## References
- https://github.com/mbuesch/letmein/security/advisories/GHSA-jpv7-p47h-f43j
- https://nvd.nist.gov/vuln/detail/CVE-2025-52570
- https://github.com/mbuesch/letmein/commit/43207cd77580410d97165d1e3c07361ba6f3558c
- https://github.com/mbuesch/letmein
