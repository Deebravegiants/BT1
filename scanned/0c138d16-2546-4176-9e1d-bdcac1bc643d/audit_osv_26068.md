# [M] jq has stack-based buffer overflow in decNaNs

## Summary
Severity: Medium
Advisory: CVE-2023-50268
Aliases: GHSA-7hmr-442f-qc8j
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-50268
Type: osv

## Details
jq is a command-line JSON processor. Version 1.7 is vulnerable to stack-based buffer overflow in builds using decNumber. Version 1.7.1 contains a patch for this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/12/15/10
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=64771
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50268.json
- https://github.com/jqlang/jq/security/advisories/GHSA-7hmr-442f-qc8j
- https://nvd.nist.gov/vuln/detail/CVE-2023-50268
- https://github.com/jqlang/jq/commit/c9a51565214eece8f1053089739aea73145bfd6b
- https://github.com/jqlang/jq/pull/2804
