# [M] ALPINE-CVE-2019-13615

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13615
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13615
Type: osv

## Affected
- Alpine:v3.10: `libebml` — affected >=0 <1.3.6-r0
- Alpine:v3.11: `libebml` — affected >=0 <1.3.6-r0
- Alpine:v3.7: `libebml` — affected >=0 <1.3.5-r1
- Alpine:v3.8: `libebml` — affected >=0 <1.3.6-r0
- Alpine:v3.9: `libebml` — affected >=0 <1.3.6-r0

## Details
libebml before 1.3.6, as used in the MKV module in VideoLAN VLC Media Player binaries before 3.0.3, has a heap-based buffer over-read in EbmlElement::FindNextElement.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13615
