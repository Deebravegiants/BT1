# [C] Ariadne Component Library vulnerable to Server-Side Request Forgery

## Summary
Severity: Critical
Advisory: GHSA-qr97-v87p-x965
CVE: CVE-2017-20157
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-31
Source: https://github.com/advisories/GHSA-qr97-v87p-x965
Type: github-advisory

## Affected
- Packagist: `arc/web` — affected >=0 <3.0

## Details
A vulnerability was found in Ariadne Component Library up to 2.x. It has been classified as critical. Affected is an unknown function of the file src/url/Url.php. The manipulation leads to server-side request forgery. Upgrading to version 3.0 can address this issue. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-217140.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20157
- https://github.com/Ariadne-CMS/arc-web/commit/1feb1cc11e6c9f218408f15f53f537ea0d788656
- https://github.com/Ariadne-CMS/arc-web
- https://github.com/Ariadne-CMS/arc-web/releases/tag/3.0
- https://vuldb.com/?ctiid.217140
- https://vuldb.com/?id.217140
