# [M] CRI-O: Maliciously structured checkpoint file can gain arbitrary node access

## Summary
Severity: Medium
Advisory: GHSA-7p9f-6x8j-gxxp
CVE: CVE-2024-8676
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-26
Source: https://github.com/advisories/GHSA-7p9f-6x8j-gxxp
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.29.11
- Go: `github.com/cri-o/cri-o` — affected >=1.30.0 <1.30.8
- Go: `github.com/cri-o/cri-o` — affected >=1.31.0 <1.31.3

## Details
### Impact

### Patches
1.31.1, 1.30.6, 1.29.8

### Workarounds
set `enable_criu_support = false` 

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-7p9f-6x8j-gxxp
- https://nvd.nist.gov/vuln/detail/CVE-2024-8676
- https://github.com/cri-o/cri-o/commit/e8e7dcb7838d11b5157976bf3e31a5840bb77de7
- https://access.redhat.com/errata/RHBA-2024:10826
- https://access.redhat.com/errata/RHSA-2025:0648
- https://access.redhat.com/errata/RHSA-2025:1908
- https://access.redhat.com/errata/RHSA-2025:3297
- https://access.redhat.com/errata/RHSA-2025:4211
- https://access.redhat.com/errata/RHSA-2025:9765
- https://access.redhat.com/security/cve/CVE-2024-8676
- https://bugzilla.redhat.com/show_bug.cgi?id=2313842
- https://github.com/cri-o/cri-o
