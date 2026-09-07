# [H] Silverstripe CMS information disclosure

## Summary
Severity: High
Advisory: GHSA-gm5x-hpmw-xpxg
CVE: CVE-2020-6164
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gm5x-hpmw-xpxg
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=0
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.4.7
- Packagist: `silverstripe/framework` — affected >=4.5.0 <4.5.4

## Details
In SilverStripe through 4.5.0, a specific URL path configured by default through the silverstripe/framework module can be used to disclose the fact that a domain is hosting a Silverstripe application. There is no disclosure of the specific version. The functionality on this URL path is limited to execution in a CLI context, and is not known to present a vulnerability through web-based access. As a side-effect, this preconfigured path also blocks the creation of other resources on this path (e.g. a page).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-6164
- https://github.com/silverstripe/silverstripe-framework/commit/91d30db88f68b9b87980ef9a59e208a81980b72c
- https://github.com/silverstripe/silverstripe-framework/commit/cce2b1630937895aa28c2914837651e7cd56d74b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2020-6164.yaml
- https://github.com/silverstripe/silverstripe-cms
- https://www.silverstripe.org/download/security-releases/CVE-2020-6164
