# [H] NextCloud Cookbook's pull-checks.yml workflow is vulnerable to OS Command Injection

## Summary
Severity: High
Advisory: CVE-2023-31128
Aliases: GHSA-c5pc-mf2f-xq8h
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-31128
Type: osv

## Details
NextCloud Cookbook is a recipe library app. Prior to commit a46d9855 on the `master` branch and commit 489bb744 on the `main-0.9.x` branch, the `pull-checks.yml` workflow is vulnerable to command injection attacks because of using an untrusted `github.head_ref` field. The `github.head_ref` value is an attacker-controlled value. Assigning the value to `zzz";echo${IFS}"hello";#` can lead to command injection. Since the permission is not restricted, the attacker has a write-access to the repository. This issue is fixed in commit a46d9855 on the `master` branch and commit 489bb744 on the `main-0.9.x` branch. There is no risk for the user of the app within the NextCloud server. This only affects the main repository and possible forks of it. Those who have forked the NextCloud Cookbook repository should make sure their forks are on the latest version to prevent code injection attacks and similar.

## References
- https://github.com/nextcloud/cookbook/blob/a14d6ffc4d45e1447556f68606129dfd6c1505cf/.github/workflows/pull-checks.yml#L67
- https://securitylab.github.com/research/github-actions-untrusted-input/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31128.json
- https://github.com/nextcloud/cookbook/security/advisories/GHSA-c5pc-mf2f-xq8h
- https://nvd.nist.gov/vuln/detail/CVE-2023-31128
- https://github.com/nextcloud/cookbook/commit/489bb744
- https://github.com/nextcloud/cookbook/commit/a46d98559e2c64292da9ffb06138cccc2e50ae1b
