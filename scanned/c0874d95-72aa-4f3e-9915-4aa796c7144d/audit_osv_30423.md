# [M] Nextcloud Server is missing password confirmation when changing external storage options

## Summary
Severity: Medium
Advisory: CVE-2024-52518
Aliases: GHSA-vrhf-532w-99rg
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52518
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. After an attacker got access to the session of a user or administrator, the attacker would be able to create, change or delete external storages without having to confirm the password. It is recommended that the Nextcloud Server is upgraded to 28.0.12, 29.0.9 or 30.0.2.

## References
- https://hackerone.com/reports/2602973
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52518.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vrhf-532w-99rg
- https://nvd.nist.gov/vuln/detail/CVE-2024-52518
- https://github.com/nextcloud/server/pull/48373
- https://github.com/nextcloud/server/pull/48788
- https://github.com/nextcloud/server/pull/48992
