# [M] quic-go affected by an ICMP Packet Too Large Injection Attack on Linux

## Summary
Severity: Medium
Advisory: GHSA-px8v-pp82-rcvr
CVE: CVE-2024-53259
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-px8v-pp82-rcvr
Type: github-advisory

## Affected
- Go: `github.com/quic-go/quic-go` — affected >=0 <0.48.2

## Details
### Impact
An off-path attacker can inject an ICMP Packet Too Large packet. Since affected quic-go versions used `IP_PMTUDISC_DO`, the kernel would then return a "message too large" error on `sendmsg`, i.e. when quic-go attempts to send a packet that exceeds the MTU claimed in that ICMP packet.

By setting this value to smaller than 1200 bytes (the minimum MTU for QUIC), the attacker can disrupt a QUIC connection. Crucially, this can be done after completion of the handshake, thereby circumventing any TCP fallback that might be implemented on the application layer (for example, many browsers fall back to HTTP over TCP if they're unable to establish a QUIC connection).

As far as I understand, the kernel tracks the MTU per 4-tuple, so the attacker needs to at least know the client's IP and port tuple to mount an attack (assuming that it knows the server's IP and port).

### Patches

The fix is easy: Use `IP_PMTUDISC_PROBE` instead of `IP_PMTUDISC_DO`. This socket option only sets the DF bit, but disables the kernel's MTU tracking.

_Has the problem been patched? What versions should users upgrade to?_

Fixed in https://github.com/quic-go/quic-go/pull/4729
Released in https://github.com/quic-go/quic-go/releases/tag/v0.48.2

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Use iptables to drop ICMP Unreachable packets.

### References

_Are there any links users can visit to find out more?_

This bug was discovered while doing research for my new IETF draft on IP fragmentation: https://datatracker.ietf.org/doc/draft-seemann-tsvwg-udp-fragmentation/

## References
- https://github.com/quic-go/quic-go/security/advisories/GHSA-px8v-pp82-rcvr
- https://nvd.nist.gov/vuln/detail/CVE-2024-53259
- https://github.com/quic-go/quic-go/pull/4729
- https://github.com/quic-go/quic-go/commit/ca31dd355cbe5fc6c5807992d9d1149c66c96a50
- https://github.com/quic-go/quic-go
- https://github.com/quic-go/quic-go/releases/tag/v0.48.2
