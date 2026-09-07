# [M] Cross-site Scripting in DaSchTour matomo-mediawiki-extension

## Summary
Severity: Medium
Advisory: GHSA-hc67-v29c-7g78
CVE: CVE-2017-20175
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-05
Source: https://github.com/advisories/GHSA-hc67-v29c-7g78
Type: github-advisory

## Affected
- Packagist: `mediawiki/matomo` — affected >=0 <2.4.3

## Details
A vulnerability classified as problematic has been found in DaSchTour matomo-mediawiki-extension up to 2.4.2. This affects an unknown part of the file Piwik.hooks.php of the component Username Handler. The manipulation leads to cross site scripting. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 2.4.3 is able to address this issue. The name of the patch is 681324e4f518a8af4bd1f93867074c728eb9923d. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-220203.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20175
- https://github.com/DaSchTour/matomo-mediawiki-extension/pull/17
- https://github.com/DaSchTour/matomo-mediawiki-extension/commit/681324e4f518a8af4bd1f93867074c728eb9923d
- https://github.com/DaSchTour/matomo-mediawiki-extension
- https://github.com/DaSchTour/matomo-mediawiki-extension/releases/tag/v2.4.3
- https://vuldb.com/?ctiid.220203
- https://vuldb.com/?id.220203
