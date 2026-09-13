# [M] Apache NimBLE: Mesh Proxy SAR reassembly unbounded append and unchecked failure

## Summary
Severity: Medium
Advisory: CVE-2026-46452
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-46452
Type: osv

## Details
Improper Input Validation vulnerability in Apache NimBLE in Mesh Proxy SAR reassembly could result in passing broken data toward application resulting in memory pressure and unstable parsing behavior.

This issue affects Apache NimBLE: through 1.9.0.

Users are recommended to upgrade to version 1.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46452.json
- https://lists.apache.org/thread/ym80ogxj3398khvxxogxroz4gvgw3ssg
- https://nvd.nist.gov/vuln/detail/CVE-2026-46452
- https://github.com/apache/mynewt-nimble/commit/593f95227a4073efde840a9bb34614929dfa7ed1
