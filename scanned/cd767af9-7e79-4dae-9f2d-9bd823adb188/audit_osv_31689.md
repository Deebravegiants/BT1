# [H] ClipBucket V5 Unauthenticated Template Directory Update to Denial-of-Service

## Summary
Severity: High
Advisory: CVE-2025-21623
Aliases: GHSA-ffhj-hprx-7qvr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-21623
Type: osv

## Details
ClipBucket V5 provides open source video hosting with PHP. Prior to 5.5.1 - 238, ClipBucket V5 allows unauthenticated attackers to change the template directory via a directory traversal, which results in a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21623.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-ffhj-hprx-7qvr
- https://nvd.nist.gov/vuln/detail/CVE-2025-21623
- https://github.com/MacWarrior/clipbucket-v5/commit/75d663f010cd8569eb9e278f030838174fb30188
