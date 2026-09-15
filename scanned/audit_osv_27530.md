# [M] jq has signed integer overflow in jv.c:jvp_array_write

## Summary
Severity: Medium
Advisory: CVE-2024-23337
Aliases: GHSA-2q6r-344g-cx46
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/CVE-2024-23337
Type: osv

## Details
jq is a command-line JSON processor. In versions up to and including 1.7.1, an integer overflow arises when assigning value using an index of 2147483647, the signed integer limit. This causes a denial of service. Commit de21386681c0df0104a99d9d09db23a9b2a78b1e contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23337.json
- https://github.com/jqlang/jq/security/advisories/GHSA-2q6r-344g-cx46
- https://nvd.nist.gov/vuln/detail/CVE-2024-23337
- https://github.com/jqlang/jq/issues/3262
- https://github.com/jqlang/jq/commit/de21386681c0df0104a99d9d09db23a9b2a78b1e
