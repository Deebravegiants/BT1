# [M] Jenkins Role-based Authorization Strategy Plugin grants permissions even after they’ve been disabled

## Summary
Severity: Medium
Advisory: GHSA-436g-2f92-cvhh
CVE: CVE-2023-28668
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-436g-2f92-cvhh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:role-strategy` — affected >=0 <587.588.v850a_20a_30162

## Details
Permissions in Jenkins can be enabled and disabled. Some permissions are disabled by default, e.g., Overall/Manage or Item/Extended Read. Disabled permissions cannot be granted directly, only through greater permissions that imply them (e.g., Overall/Administer or Item/Configure).

Role-based Authorization Strategy Plugin 587.v2872c41fa_e51 and earlier grants permissions even after they’ve been disabled.

This allows attackers to have greater access than they’re entitled to after the following operations took place:

A permission is granted to attackers directly or through groups.

The permission is disabled, e.g., through the script console.

Role-based Authorization Strategy Plugin 587.588.v850a_20a_30162 does not grant disabled permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28668
- https://github.com/jenkinsci/role-strategy-plugin/commit/850a20a3016276d0c0ba4898a876c113a9191da4
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-3053
