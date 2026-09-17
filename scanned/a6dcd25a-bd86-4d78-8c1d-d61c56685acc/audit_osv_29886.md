# [M] Scout contains insufficient output escaping of attachment names

## Summary
Severity: Medium
Advisory: CVE-2024-47531
Aliases: GHSA-24xv-q29v-3h6r
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-09-30
Source: https://osv.dev/vulnerability/CVE-2024-47531
Type: osv

## Details
Scout is a web-based visualizer for VCF-files. Due to the lack of sanitization in the filename, it is possible bypass intended file extension and make users download malicious files with any extension. With malicious content injected inside the file data and users unknowingly downloading it and opening may lead to the compromise of users' devices or data. This vulnerability is fixed in 4.89.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47531.json
- https://github.com/Clinical-Genomics/scout/security/advisories/GHSA-24xv-q29v-3h6r
- https://nvd.nist.gov/vuln/detail/CVE-2024-47531
- https://github.com/Clinical-Genomics/scout/commit/f59e50f8ea596e641da8a0e9c7a33c0696bcbea5
