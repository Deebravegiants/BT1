# [M] zeroconf has unbounded recursion in DNS compression-pointer decoder that allows LAN-local denial of service

## Summary
Severity: Medium
Advisory: GHSA-9pgc-3ccv-5297
CVE: CVE-2026-47180
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-9pgc-3ccv-5297
Type: github-advisory

## Affected
- PyPI: `zeroconf` — affected >=0 <0.149.5

## Details
### Impact

`DNSIncoming._decode_labels_at_offset` recurses once per DNS-name compression pointer (RFC 1035 §4.1.4). Pointer cycles and label counts were capped, but the chain length of unique forward pointers was not. A single ~3 kB mDNS packet carrying ~1500 chained pointers drives the recursion past CPython's default limit, and `RecursionError` was not listed in `DECODE_EXCEPTIONS`, so it escaped `DNSIncoming.__init__` and was logged by asyncio's default exception handler.

Any unauthenticated host on the local link (UDP/5353, `224.0.0.251` / `ff02::fb`) can degrade the mDNS listener; that includes a guest on the same Wi-Fi, a compromised IoT device, or a container on a shared bridge. Replaying at a few hertz produces sustained CPU burn and log flooding, and mDNS-dependent features (HomeKit, Chromecast/Matter, AirPlay, printers) degrade while the attack is in flight.

### Patches
Fixed in `zeroconf` 0.149.5 ([PR #1719](https://github.com/python-zeroconf/python-zeroconf/pull/1719)).
Upgrade to `>= 0.149.5`.

### Workarounds
There is no in-process workaround; upgrading is the fix. Otherwise, restrict mDNS (UDP/5353) to trusted Layer-2 segments via AP client isolation, guest-network separation, or host firewall rules.

### Resources
- [PR #1719](https://github.com/python-zeroconf/python-zeroconf/pull/1719), fix
- [Issue #1713](https://github.com/python-zeroconf/python-zeroconf/issues/1713), public tracking issue
- [RFC 1035 §4.1.4](https://www.rfc-editor.org/rfc/rfc1035#section-4.1.4), [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762), [CWE-674](https://cwe.mitre.org/data/definitions/674.html)

## References
- https://github.com/python-zeroconf/python-zeroconf/security/advisories/GHSA-9pgc-3ccv-5297
- https://github.com/python-zeroconf/python-zeroconf/issues/1713
- https://github.com/python-zeroconf/python-zeroconf/pull/1719
- https://github.com/python-zeroconf/python-zeroconf
