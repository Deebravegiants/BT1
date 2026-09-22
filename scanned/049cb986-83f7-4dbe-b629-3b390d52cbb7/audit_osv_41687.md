# [M] XQUIC Improper STREAM Frame Validation in Initial/Handshake Packets

## Summary
Severity: Medium
Advisory: CVE-2026-6328
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-6328
Type: osv

## Details
Improper input validation, Improper verification of cryptographic signature vulnerability in XQUIC Project XQUIC xquic on Linux (QUIC protocol implementation, packet processing module, STREAM frame handler modules) allows Protocol Manipulation.This issue affects XQUIC: through 1.8.3.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6328.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6328
- https://github.com/alibaba/xquic/commit/4764604a0e487eeb49338b4498aecda2194eae84
- https://github.com/alibaba/xquic
