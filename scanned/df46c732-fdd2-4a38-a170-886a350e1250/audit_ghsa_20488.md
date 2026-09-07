# [H] Umbraco ApplicationURL Overwrite

## Summary
Severity: High
Advisory: GHSA-jrmq-rv9w-63rv
CVE: CVE-2022-22690
CWE: CWE-444
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-jrmq-rv9w-63rv
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Core` — affected >=0 <9.2.0

## Details
Within the Umbraco CMS, a configuration element named "UmbracoApplicationUrl" (or just "ApplicationUrl") is used whenever application code needs to build a URL pointing back to the site. For example, when a user resets their password and the application builds a password reset URL or when the administrator invites users to the site. For Umbraco versions less than 9.2.0, if the Application URL is not specifically configured, the attacker can manipulate this value and store it persistently affecting all users for components where the "UmbracoApplicationUrl" is used. For example, the attacker is able to change the URL users receive when resetting their password so that it points to the attackers server, when the user follows this link the reset token can be intercepted by the attacker resulting in account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22690
- https://appcheck-ng.com/umbraco-applicationurl-overwrite-persistent-password-reset-poison-cve-2022-22690-cve-2022-22691
- https://github.com/umbraco/Umbraco-CMS
