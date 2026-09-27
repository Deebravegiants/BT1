# [M] jq has heap-buffer-overflow vulnerability in the function decToString in decNumber.c

## Summary
Severity: Medium
Advisory: CVE-2023-50246
Aliases: GHSA-686w-5m7m-54vc
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-50246
Type: osv

## Details
jq is a command-line JSON processor. Version 1.7 is vulnerable to heap-based buffer overflow. Version 1.7.1 contains a patch for this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/12/15/10
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=64574
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50246.json
- https://github.com/jqlang/jq/security/advisories/GHSA-686w-5m7m-54vc
- https://nvd.nist.gov/vuln/detail/CVE-2023-50246
- https://github.com/jqlang/jq/commit/71c2ab509a8628dbbad4bc7b3f98a64aa90d3297
