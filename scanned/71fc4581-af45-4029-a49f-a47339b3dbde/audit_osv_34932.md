# [M] Nextcloud Tables app share information not limited to relevant users

## Summary
Severity: Medium
Advisory: CVE-2025-66513
Aliases: GHSA-2cwj-qp49-4xfw
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66513
Type: osv

## Details
Nextcloud Tables allows you to create your own tables with individual columns. Prior to 0.8.9, 0.9.6, and 1.0.1, the information which table (numeric ID) is shared with which groups or users and the respective permissions was not limited to privileged users. This vulnerability is fixed in 0.8.9, 0.9.6, and 1.0.1.

## References
- https://hackerone.com/reports/3334165
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66513.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2cwj-qp49-4xfw
- https://nvd.nist.gov/vuln/detail/CVE-2025-66513
- https://github.com/nextcloud/tables/commit/b92b9560b1e70a02b103a7aeb9e22e2ab5231873
- https://github.com/nextcloud/tables/pull/2148
