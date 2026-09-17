# [H] ngtcp2 has a qlog transport parameter serialization stack buffer overflow

## Summary
Severity: High
Advisory: CVE-2026-40170
Aliases: GHSA-f523-465f-8c8f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40170
Type: osv

## Details
ngtcp2 is a C implementation of the IETF QUIC protocol. In versions prior to 1.22.1, ngtcp2_qlog_parameters_set_transport_params() serializes peer transport parameters into a fixed 1024-byte stack buffer without bounds checking. When qlog is enabled, a remote peer can send sufficiently large transport parameters during the QUIC handshake to cause writes beyond the buffer boundary, resulting in a stack buffer overflow. This affects deployments that enable the qlog callback and process untrusted peer transport parameters. This issue has been fixed in version 1.22.1. If developers are unable to immediately upgrade, they can disable the qlog on client.

## References
- http://www.openwall.com/lists/oss-security/2026/04/17/12
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40170.json
- https://access.redhat.com/errata/RHSA-2026:22963
- https://access.redhat.com/errata/RHSA-2026:25049
- https://access.redhat.com/errata/RHSA-2026:9113
- https://access.redhat.com/security/cve/CVE-2026-40170
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40170.json
- https://github.com/ngtcp2/ngtcp2/security/advisories/GHSA-f523-465f-8c8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40170
- https://bugzilla.redhat.com/show_bug.cgi?id=2459061
- https://github.com/ngtcp2/ngtcp2/commit/708a7640c1f48fb8ffb540c4b8ea5b4c1dfb8ee5
