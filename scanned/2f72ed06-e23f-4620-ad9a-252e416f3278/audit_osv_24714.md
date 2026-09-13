# [M] Failure to Invalidate Session on Logout in DataHub

## Summary
Severity: Medium
Advisory: CVE-2023-25562
Aliases: GHSA-3974-hxjh-m3jj
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-02-10
Source: https://osv.dev/vulnerability/CVE-2023-25562
Type: osv

## Details
DataHub is an open-source metadata platform. In versions of DataHub prior to 0.8.45 Session cookies are only cleared on new sign-in events and not on logout events. Any authentication checks using the `AuthUtils.hasValidSessionCookie()` method could be bypassed by using a cookie from a logged out session, as a result any logged out session cookie may be accepted as valid and therefore lead to an authentication bypass to the system. Users are advised to upgrade. There are no known workarounds for this issue. This vulnerability was discovered and reported by the GitHub Security lab and is tracked as GHSL-2022-083.

## References
- https://github.com/datahub-project/datahub/blob/aa146db611e3a4ca3aa17bb740783f789d4444d3/datahub-frontend/app/auth/AuthUtils.java#L78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25562.json
- https://github.com/datahub-project/datahub/security/advisories/GHSA-3974-hxjh-m3jj
- https://nvd.nist.gov/vuln/detail/CVE-2023-25562
