# [M] zeroconf has unbounded DNS record cache that allows LAN-local memory exhaustion via multicast flood

## Summary
Severity: Medium
Advisory: GHSA-rfg2-pjw2-56x2
CVE: CVE-2026-47184
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-rfg2-pjw2-56x2
Type: github-advisory

## Affected
- PyPI: `zeroconf` — affected >=0 <0.149.7

## Details
### Impact

`DNSCache._async_add` inserted every response record into `cache`, `_expirations`, `_expire_heap`, and `service_cache` with no cap on entry count. The only pre-existing protection was a PTR TTL floor (`_DNS_PTR_MIN_TTL = 1125` s, RFC 6762 §10), which actually *prolonged* attacker-injected records, and a periodic `async_expire` on `_CACHE_CLEANUP_INTERVAL = 10` s that could not keep up with a flood.

Any unauthenticated host on the local link (UDP/5353, `224.0.0.251` / `ff02::fb`) can multicast valid mDNS responses with unique names (RFC 6762 §11 allows up to 253 bytes each) and watch them accumulate. On memory-constrained deployments (Home Assistant on Raspberry-Pi-class hardware is the canonical victim) sustained traffic OOM-kills the process; under lighter load, every cache lookup and every periodic expiry pass grows linearly slower, starving asyncio and breaking unrelated zeroconf consumers (discovery, registration, ServiceBrowser callbacks). A second variant — re-multicasting cached records with shifting TTLs — grows `_expire_heap` unbounded between cleanup runs without touching `cache` or `_total_records`.

### Patches

Fixed in `zeroconf` 0.149.6 ([PR #1718](https://github.com/python-zeroconf/python-zeroconf/pull/1718)). Upgrade to `>= 0.149.6`.

### Workarounds

There is no in-process workaround; upgrading is the fix. Otherwise, restrict mDNS (UDP/5353) to trusted Layer-2 segments via AP client isolation, guest-network separation, or host firewall rules.

### Resources

- [PR #1718](https://github.com/python-zeroconf/python-zeroconf/pull/1718), fix
- [Issue #1715](https://github.com/python-zeroconf/python-zeroconf/issues/1715), public tracking issue
- [RFC 6762 §10](https://www.rfc-editor.org/rfc/rfc6762#section-10), [RFC 6762 §11](https://www.rfc-editor.org/rfc/rfc6762#section-11), [CWE-400](https://cwe.mitre.org/data/definitions/400.html)

## References
- https://github.com/python-zeroconf/python-zeroconf/security/advisories/GHSA-rfg2-pjw2-56x2
- https://github.com/python-zeroconf/python-zeroconf/issues/1715
- https://github.com/python-zeroconf/python-zeroconf/pull/1718
- https://github.com/python-zeroconf/python-zeroconf
