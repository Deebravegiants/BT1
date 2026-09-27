# [H] Coturn: Misaligned Memory Access in coturn STUN Attribute Parser (Remote DoS on ARM64)

## Summary
Severity: High
Advisory: CVE-2026-40613
Aliases: GHSA-j662-9wcj-mf36
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40613
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.10.0, the STUN/TURN attribute parsing functions in coturn perform unsafe pointer casts from uint8_t * to uint16_t * without alignment checks. When processing a crafted STUN message with odd-aligned attribute boundaries, this results in misaligned memory reads at ns_turn_msg.c. On ARM64 architectures (AArch64) with strict alignment enforcement, this causes a SIGBUS signal that immediately kills the turnserver process. An unauthenticated remote attacker can crash any ARM64 coturn deployment by sending a single crafted UDP packet. This vulnerability is fixed in 4.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40613.json
- https://github.com/coturn/coturn/security/advisories/GHSA-j662-9wcj-mf36
- https://nvd.nist.gov/vuln/detail/CVE-2026-40613
