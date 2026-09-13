# [H] Privilege escalation in rbac

## Summary
Severity: High
Advisory: GHSA-5v95-v8c8-3rh6
CVE: CVE-2021-22538
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-5v95-v8c8-3rh6
Type: github-advisory

## Affected
- Go: `github.com/google/exposure-notifications-verification-server` — affected >=0 <0.23.1

## Details
### Impact
Using a carefully crafted request or malicious proxy, a user with `UserWrite` permissions could create another user with higher privileges than their own due to insufficient checks on the allowed set of permissions. The event would be captured in the Event Log.

### Patches
The issue has been fixed in 0.24.0 and 0.23.1.

### Workarounds
For users who are unable to upgrade, we recommend auditing users who have `UserWrite` permissions and regularly reviewing the Event Log for malicious activity.

### Kudos
Thank you to Michael Mazzolini (Ethical Hacker at WHO) for finding and disclosing this vulnerability.

## References
- https://github.com/google/exposure-notifications-verification-server/security/advisories/GHSA-5v95-v8c8-3rh6
- https://nvd.nist.gov/vuln/detail/CVE-2021-22538
- https://github.com/google/exposure-notifications-verification-server/commit/eb8cf40b12dbe79304f1133c06fb73419383cd95
- https://github.com/google/exposure-notifications-verification-server/releases/tag/v0.23.1
- https://github.com/google/exposure-notifications-verification-server/releases/tag/v0.24.0
