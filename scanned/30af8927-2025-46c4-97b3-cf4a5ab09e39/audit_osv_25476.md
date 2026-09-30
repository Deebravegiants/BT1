# [M] User login confusion with SSO in warpgate

## Summary
Severity: Medium
Advisory: CVE-2023-37268
Aliases: GHSA-868r-97g5-r9g4
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/CVE-2023-37268
Type: osv

## Details
Warpgate is an SSH, HTTPS and MySQL bastion host for Linux that doesn't need special client apps. When logging in as a user with SSO enabled an attacker may authenticate as an other user. Any user account which does not have a second factor enabled could be compromised. This issue has been addressed in commit `8173f6512a` and in releases starting with version 0.7.3. Users are advised to upgrade. Users unable to upgrade should require their users to use a second factor in authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37268.json
- https://github.com/warp-tech/warpgate/security/advisories/GHSA-868r-97g5-r9g4
- https://nvd.nist.gov/vuln/detail/CVE-2023-37268
- https://github.com/warp-tech/warpgate/commit/8173f6512ab6183fa5edc5c9a5f3760b8979271e
