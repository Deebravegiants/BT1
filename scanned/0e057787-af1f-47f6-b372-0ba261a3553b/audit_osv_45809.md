# [H] JLSEC-2026-352

## Summary
Severity: High
Advisory: JLSEC-2026-352
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-352
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <2.0.0+0

## Details
HDF5 is software for managing data. Prior to version 1.14.4-2, an attacker who can control an `h5` file parsed by HDF5 can trigger a write-based heap buffer overflow condition. This can lead to a denial-of-service condition, and potentially further issues such as remote code execution depending on the practical exploitability of the heap overflow against modern operating systems. Real-world exploitability of this issue in terms of remote-code execution is currently unknown. Version 1.14.4-2 fixes the issue.

## References
- https://access.redhat.com/security/cve/CVE-2026-26200
- https://bugzilla.redhat.com/show_bug.cgi?id=2441088
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-5p2m-j456-9mr2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-26200.json
