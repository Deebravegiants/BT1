# [H] Umbraco Affected by Vertical Privilege Escalation via Missing Authorization Checks

## Summary
Severity: High
Advisory: GHSA-rhcg-3h8r-v6vp
CVE: CVE-2026-31834
CWE: CWE-269
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-rhcg-3h8r-v6vp
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=15.3.1 <16.5.1
- NuGet: `Umbraco.Cms` — affected >=17.0.0 <17.2.2

## Details
### Description
A privilege escalation vulnerability has been identified in Umbraco CMS. Under certain conditions, authenticated backoffice users with permission to manage users, may be able to elevate their privileges due to insufficient authorization enforcement when modifying user group memberships.

The affected functionality does not properly validate whether a user has sufficient privileges to assign highly privileged roles.

### Impact
An authenticated backoffice user may be able to escalate their privileges to Administrator level.

Successful exploitation results in full administrative control of the affected Umbraco CMS instance, including unrestricted access to content, user management, and configuration settings.

The impact is significantly mitigated by the fact that this can only be exploited by a user that has already been given access to the "Users" section in the CMS.  For most Umbraco setups, such users are already also "Administrators".

### Patches
The issue is patched in 16.5.1 and 17.2.2.

### Workarounds
There is no workaround other than upgrading for setups where they want to have users with permission for the "Users" section without also being content with those users also being part of the "Administrators" user group.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-rhcg-3h8r-v6vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-31834
- https://github.com/umbraco/Umbraco-CMS
