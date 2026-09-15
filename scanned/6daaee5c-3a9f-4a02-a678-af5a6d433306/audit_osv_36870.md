# [H] HDF5 Affected by H5T__conv_struct_opt Heap Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-26200
Aliases: GHSA-5p2m-j456-9mr2
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-26200
Type: osv

## Details
HDF5 is software for managing data. Prior to version 1.14.4-2, an attacker who can control an `h5` file parsed by HDF5 can trigger a write-based heap buffer overflow condition. This can lead to a denial-of-service condition, and potentially further issues such as remote code execution depending on the practical exploitability of the heap overflow against modern operating systems. Real-world exploitability of this issue in terms of remote-code execution is currently unknown. Version 1.14.4-2 fixes the issue.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-26200.json
- https://access.redhat.com/security/cve/CVE-2026-26200
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26200.json
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-5p2m-j456-9mr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-26200
- https://bugzilla.redhat.com/show_bug.cgi?id=2441088
