# [H] Umbraco Persistent Password Reset Poison

## Summary
Severity: High
Advisory: GHSA-r8pr-83cc-ccv7
CVE: CVE-2022-22691
CWE: CWE-444, CWE-640
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-r8pr-83cc-ccv7
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Core` — affected >=0 <9.2.0

## Details
The password reset component deployed within Umbraco uses the hostname supplied within the request host header when building a password reset URL. It may be possible to manipulate the URL sent to Umbraco users when so that it points to the attackers server thereby disclosing the password reset token if/when the link is followed. A related vulnerability (CVE-2022-22690) could allow this flaw to become persistent so that all password reset URLs are affected persistently following a successful attack. See the AppCheck advisory for further information and associated caveats.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22691
- https://appcheck-ng.com/umbraco-applicationurl-overwrite-persistent-password-reset-poison-cve-2022-22690-cve-2022-22691
- https://github.com/umbraco/Umbraco-CMS
