# [H] EVerest's unchecked SLAC payload length causes stack overflow in HomeplugMessage::setup_payload

## Summary
Severity: High
Advisory: CVE-2026-22790
Aliases: GHSA-wh8w-7cfc-gq7m
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-22790
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, `HomeplugMessage::setup_payload` trusts `len` after an `assert`; in release builds the check is removed, so oversized SLAC payloads are `memcpy`'d into a ~1497-byte stack buffer, corrupting the stack and enabling remote code execution from network-provided frames. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22790.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-wh8w-7cfc-gq7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22790
