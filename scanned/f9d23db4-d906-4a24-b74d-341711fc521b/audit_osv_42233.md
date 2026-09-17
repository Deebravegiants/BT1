# [H] gopacket: Multiple layer decoders panic on crafted packets (out-of-bounds/underflow) enabling unauthenticated remote DoS via DecodingLayerParser

## Summary
Severity: High
Advisory: CVE-2026-65819
Aliases: GHSA-8mcr-459q-5mx2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-65819
Type: osv

## Details
gopacket provides packet processing capabilities for Go. Through version 1.7.0, multiple layer decoders use attacker-controlled lengths, counts, or offsets before validating them against packet buffers, allowing a crafted packet decoded through DecodingLayerParser or DecodeFromBytes to trigger an unrecovered panic and remotely deny service.  A patch commit is available at 210f25f.

## References
- https://github.com/gopacket/gopacket/releases/tag/v1.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65819.json
- https://github.com/gopacket/gopacket/security/advisories/GHSA-8mcr-459q-5mx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-65819
- https://github.com/gopacket/gopacket/commit/210f25fb9b3ca1af2eb649936f78ad6991b6c9c5
