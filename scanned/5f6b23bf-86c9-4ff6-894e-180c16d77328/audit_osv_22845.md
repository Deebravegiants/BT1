# [M] Metabase vulnerable to circumvention of Locked parameter in Signed Embedding

## Summary
Severity: Medium
Advisory: CVE-2022-39358
Aliases: GHSA-8qgm-9mj6-36h3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-39358
Type: osv

## Details
Metabase is data visualization software. Prior to versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, and 1.42.6, it was possible to circumvent locked parameters when requesting data for a question in an embedded dashboard by constructing a malicious request to the backend. This issue is patched in versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, and 1.42.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39358.json
- https://github.com/metabase/metabase/security/advisories/GHSA-8qgm-9mj6-36h3
- https://nvd.nist.gov/vuln/detail/CVE-2022-39358
