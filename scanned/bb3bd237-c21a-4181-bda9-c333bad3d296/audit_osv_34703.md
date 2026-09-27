# [M] ClipBucket v5: SQL Injection possible through ClipBucket Custom Fields plugin

## Summary
Severity: Medium
Advisory: CVE-2025-64114
Aliases: GHSA-4g7x-j562-8g69
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-64114
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. Versions 5.5.2 - #151 and below allow authenticated administrators with plugin management privileges to execute arbitrary SQL commands against the database through its ClipBucket Custom Fields plugin. The vulnerabilities require the Custom Fields plugin to be installed and accessible, and can only be exploited by users with administrative access to the plugin interface. This issue is fixed in version 5.5.2 - #.

## References
- https://github.com/MacWarrior/clipbucket-v5/releases/tag/5.5.2-%23152
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64114.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-4g7x-j562-8g69
- https://nvd.nist.gov/vuln/detail/CVE-2025-64114
- https://github.com/MacWarrior/clipbucket-v5/commit/b7289923177fe533ae908654ee3cd65b63ffb008
