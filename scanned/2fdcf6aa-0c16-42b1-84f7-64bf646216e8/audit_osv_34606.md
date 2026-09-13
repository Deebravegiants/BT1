# [M] ClipBucket V5 Blind SQL injection in the Admin Panel

## Summary
Severity: Medium
Advisory: CVE-2025-62423
Aliases: GHSA-3wpr-jprj-52fc
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62423
Type: osv

## Details
ClipBucket V5 provides open source video hosting with PHP. In version5.5.2 - #140 and earlier, a Blind SQL injection vulnerability exists in the Admin Area’s “/admin_area/login_as_user.php” file. Exploiting this vulnerability requires access privileges to the Admin Area.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62423.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-3wpr-jprj-52fc
- https://nvd.nist.gov/vuln/detail/CVE-2025-62423
- https://github.com/MacWarrior/clipbucket-v5/commit/b3bf27e367f318c2afe9bd11368be9d00e272148
