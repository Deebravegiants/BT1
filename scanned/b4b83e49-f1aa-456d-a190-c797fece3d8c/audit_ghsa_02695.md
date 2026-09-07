# [H] Cross-Site Request Forgery (CSRF) can run untrusted code on Rundeck server

## Summary
Severity: High
Advisory: GHSA-3jmw-c69h-426c
CVE: CVE-2021-39133
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-3jmw-c69h-426c
Type: github-advisory

## Affected
- Maven: `org.rundeck:rundeck-core` — affected >=3.4.0 <3.4.3
- Maven: `org.rundeck:rundeck-core` — affected >=0 <3.3.14

## Details
### Impact

A user with `admin` access to the `system` resource type is potentially vulnerable to a CSRF attack that could cause the server to run untrusted code on all Rundeck editions.

### Patches
Available in Rundeck 3.4.3 and 3.3.14


### Workarounds

Please visit [https://rundeck.com/security](https://rundeck.com/security) for information about specific workarounds.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@rundeck.com](mailto:security@rundeck.com)

To report security issues to Rundeck please use the form at [https://rundeck.com/security](https://rundeck.com/security)

## References
- https://github.com/rundeck/rundeck/security/advisories/GHSA-3jmw-c69h-426c
- https://nvd.nist.gov/vuln/detail/CVE-2021-39133
- https://github.com/rundeck/rundeck/commit/67c4eedeaf9509fc0b255aff15977a5229ef13b9
- https://github.com/rundeck/rundeck
