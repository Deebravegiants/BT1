# [M] cmark-gfm out-of-bounds read in validate_protocol

## Summary
Severity: Medium
Advisory: CVE-2023-22485
Aliases: GHSA-c944-cv5f-hpvr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-01-24
Source: https://osv.dev/vulnerability/CVE-2023-22485
Type: osv

## Details
cmark-gfm is GitHub's fork of cmark, a CommonMark parsing and rendering library and program in C. In versions prior 0.29.0.gfm.7, a crafted markdown document can trigger an out-of-bounds read in the `validate_protocol` function. We believe this bug is harmless in practice, because the out-of-bounds read accesses `malloc` metadata without causing any visible damage.This vulnerability has been patched in 0.29.0.gfm.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22485.json
- https://github.com/github/cmark-gfm/security/advisories/GHSA-c944-cv5f-hpvr
- https://nvd.nist.gov/vuln/detail/CVE-2023-22485
