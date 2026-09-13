# [M] Sandbox escape for instances that have enabled transformation functions in matrix-hookshot

## Summary
Severity: Medium
Advisory: CVE-2023-43656
Aliases: GHSA-fr97-pv6w-4cj6
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-43656
Type: osv

## Details
matrix-hookshot is a Matrix bot for connecting to external services like GitHub, GitLab, JIRA, and more. Instances that have enabled transformation functions (those that have `generic.allowJsTransformationFunctions` in their config), may be vulnerable to an attack where it is possible to break out of the `vm2` sandbox and as a result Hookshot will be vulnerable to this. This problem is only likely to affect users who have allowed untrusted users to apply their own transformation functions. If you have only enabled a limited set of trusted users, this threat is reduced (though not eliminated). Version 4.5.0 and above of hookshot include a new sandbox library which should better protect users. Users are advised to upgrade. Users unable to upgrade should disable `generic.allowJsTransformationFunctions` in the config.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43656.json
- https://github.com/matrix-org/matrix-hookshot/security/advisories/GHSA-fr97-pv6w-4cj6
- https://nvd.nist.gov/vuln/detail/CVE-2023-43656
- https://github.com/matrix-org/matrix-hookshot/commit/dc126afa6af86d66aefcd23a825326f405bcc894
