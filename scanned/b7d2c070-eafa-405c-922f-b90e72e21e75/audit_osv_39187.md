# [H] FreeRDP cliprdr server heap-buffer-overflow via undersized capabilitySetLength in CB_CLIP_CAPS

## Summary
Severity: High
Advisory: CVE-2026-44420
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44420
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.26.0, a malicious RDP client can trigger a heap-buffer-overflow write in FreeRDP's server-side clipboard (cliprdr) channel by sending a CB_CLIP_CAPS PDU with a too-small capabilitySetLength. This can crash the server process (remote DoS) and may be exploitable for code execution because it corrupts heap memory. This vulnerability is fixed in 3.26.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44420.json
- https://access.redhat.com/errata/RHSA-2026:36203
- https://access.redhat.com/errata/RHSA-2026:46393
- https://access.redhat.com/security/cve/CVE-2026-44420
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44420.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mvpx-xj7r-3p3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44420
- https://bugzilla.redhat.com/show_bug.cgi?id=2483480
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-h6wq-j5mv-f3q8
