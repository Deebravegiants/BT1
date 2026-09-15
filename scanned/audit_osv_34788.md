# [M] Rallly Improper Authorization in Comment Endpoint Allows User Impersonation

## Summary
Severity: Medium
Advisory: CVE-2025-65031
Aliases: GHSA-hhfc-6gq7-rrpm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65031
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an improper authorization flaw in the comment creation endpoint allows authenticated users to impersonate any other user by altering the authorName field in the API request. This enables attackers to post comments under arbitrary usernames, including privileged ones such as administrators, potentially misleading other users and enabling phishing or social engineering attacks. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65031.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-hhfc-6gq7-rrpm
- https://nvd.nist.gov/vuln/detail/CVE-2025-65031
