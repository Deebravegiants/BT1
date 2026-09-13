# [M] Eclipse OMR : arraycmp SIMD implementation does not check if the number of bytes to compare is zero

## Summary
Severity: Medium
Advisory: CVE-2026-16243
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-16243
Type: osv

## Details
In Eclipse OMR versions up to 0.11, the arraycmp SIMD implementation for Z and P does not check if the number of bytes to compare is zero.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/195
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16243
- https://github.com/eclipse-omr/omr/pull/8348
- https://github.com/eclipse-omr/omr/pull/8349
