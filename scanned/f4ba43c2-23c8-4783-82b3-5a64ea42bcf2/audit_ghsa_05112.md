# [M] zeroconf: Unvalidated rdlength in record payload readers allows LAN-local cache corruption via crafted mDNS packet

## Summary
Severity: Medium
Advisory: GHSA-qc2x-6f54-m6h9
CVE: CVE-2026-48487
CWE: CWE-130
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-qc2x-6f54-m6h9
Type: github-advisory

## Affected
- PyPI: `zeroconf` — affected >=0 <0.149.16

## Details
### Impact

`_read_character_string` and `_read_string` in `src/zeroconf/_protocol/incoming.py` sliced `self.data[self.offset : self.offset + length]` and advanced `self.offset` by the declared `length` without checking it against `self._data_len`. Python's slice silently returns fewer bytes when the end index runs past the buffer, so a record whose 16-bit RDLENGTH (RFC 1035 §3.2.1) over-advertised by tens of kilobytes was constructed from a truncated payload, appended to `DNSIncoming._answers`, and committed to the cache before any later parse failure surfaced. The follow-up `_read_name` for the next record then failed, but the corrupt record had already entered the answer list and propagated to `DNSCache` and `ServiceInfo`.

Any unauthenticated host on the local link (UDP/5353, `224.0.0.251` / `ff02::fb`) can multicast a single mDNS response carrying a TXT, HINFO, or A/AAAA record that advertises rdlength=65535 and only a handful of real payload bytes; consumers calling `ServiceInfo.properties` then parse the truncated bytes as if they matched the wire, and downstream integrations (Home Assistant and other zeroconf-driven discovery) trust the decoded record. The bug is parser-state desync rather than RCE, but it seeds the cache with attacker-shaped key/value and address records for a TTL window and is a building block for higher-impact chains.

The impact is likely lower than the other recently released advisories as there is no additional risk of OOM so the severity was manually set to low to override the score CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (6.5, Medium) since that doesn't fully consider the mDNS threat model.

### Patches

Fixed in `zeroconf` 0.149.16 ([PR #1756](https://github.com/python-zeroconf/python-zeroconf/pull/1756)).  Note that this change originally intended to ship in 0.149.13 but we ran out of space on PyPI: see https://github.com/python-zeroconf/python-zeroconf/issues/1769

Upgrade to `>= 0.149.16`.

### Workarounds

There is no in-process workaround; upgrading is the fix. Otherwise, restrict mDNS (UDP/5353) to trusted Layer-2 segments via AP client isolation, guest-network separation, or host firewall rules.

### Resources

- [PR #1756](https://github.com/python-zeroconf/python-zeroconf/pull/1756), fix
- [Issue #1752](https://github.com/python-zeroconf/python-zeroconf/issues/1752), public tracking issue
- [RFC 1035 §3.2.1](https://www.rfc-editor.org/rfc/rfc1035#section-3.2.1), [RFC 1035 §3.3](https://www.rfc-editor.org/rfc/rfc1035#section-3.3), [CWE-130](https://cwe.mitre.org/data/definitions/130.html)

## References
- https://github.com/python-zeroconf/python-zeroconf/security/advisories/GHSA-qc2x-6f54-m6h9
- https://github.com/python-zeroconf/python-zeroconf/issues/1752
- https://github.com/python-zeroconf/python-zeroconf/pull/1756
- https://github.com/python-zeroconf/python-zeroconf
