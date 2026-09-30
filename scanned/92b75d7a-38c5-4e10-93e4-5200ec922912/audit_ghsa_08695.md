# [M] zeroconf: Unbounded exception-dedup state retains packet buffers via traceback frame locals, enabling LAN-local memory exhaustion

## Summary
Severity: Medium
Advisory: GHSA-phvx-9mgw-67r5
CVE: CVE-2026-47183
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-phvx-9mgw-67r5
Type: github-advisory

## Affected
- PyPI: `zeroconf` — affected >=0 <0.149.6

## Details
### Impact
`DNSIncoming._log_exception_debug` and the four `QuietLogger` exception-dedup methods stored an unbounded `_seen_logs` dict keyed by `str(sys.exc_info()[1])`. The seven `IncomingDecodeError` messages raised from `_read_name` / `_decode_labels_at_offset` (RFC 6762 §18 name-decoding error paths) all embed `self.source` — the peer's ephemeral source port, varying per packet — plus byte `offset` and pointer `link`, so every attacker-influenced combination produced a fresh dedup key. The stored value was the full `sys.exc_info()` triple, whose traceback's frame locals retained `self.data` (the raw inbound packet, up to 8966 bytes per RFC 6762 §17). Each unique malformed packet therefore pinned ~9 KB until process exit.

Any unauthenticated host on the local link (UDP/5353, `224.0.0.251` / `ff02::fb`) can drive memory growth at line rate; that includes a guest on the same Wi-Fi, a compromised IoT device, or a container on a shared bridge. On memory-constrained deployments (Home Assistant on Raspberry-Pi-class hardware is the canonical victim) sustained traffic trivially OOM-kills the process, and mDNS-dependent features (HomeKit, Chromecast/Matter, AirPlay, printers) degrade or fail.

### Patches
Fixed in `zeroconf` 0.149.6 ([PR #1717](https://github.com/python-zeroconf/python-zeroconf/pull/1717)). Upgrade to `>= 0.149.6`.

### Workarounds
There is no in-process workaround; upgrading is the fix. Otherwise, restrict mDNS (UDP/5353) to trusted Layer-2 segments via AP client isolation, guest-network separation, or host firewall rules.

### Resources
- [PR #1717](https://github.com/python-zeroconf/python-zeroconf/pull/1717), fix
- [Issue #1714](https://github.com/python-zeroconf/python-zeroconf/issues/1714), public tracking issue
- [RFC 6762 §17](https://www.rfc-editor.org/rfc/rfc6762#section-17), [RFC 6762 §18](https://www.rfc-editor.org/rfc/rfc6762#section-18), [CWE-400](https://cwe.mitre.org/data/definitions/400.html)

## References
- https://github.com/python-zeroconf/python-zeroconf/security/advisories/GHSA-phvx-9mgw-67r5
- https://github.com/python-zeroconf/python-zeroconf/issues/1714
- https://github.com/python-zeroconf/python-zeroconf/pull/1717
- https://github.com/python-zeroconf/python-zeroconf
