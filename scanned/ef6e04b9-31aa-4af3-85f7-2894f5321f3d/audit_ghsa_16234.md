# [M] XWiki extension license information is public, exposing instance id and license holder details

## Summary
Severity: Medium
Advisory: GHSA-4hfp-m9gv-m753
CVE: CVE-2024-26138
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-4hfp-m9gv-m753
Type: github-advisory

## Affected
- Maven: `com.xwiki.licensing:application-licensing-licensor-ui` — affected >=1.0 <1.24.2

## Details
### Impact
The licensor application includes the document `Licenses.Code.LicenseJSON` that provides information for admins regarding active licenses. This document is public and thus exposes this information publicly. The information includes the instance's id as well as first and last name and email of the license owner. This is a leak of information that isn't supposed to be public. The instance id allows associating data on the [active installs data](https://extensions.xwiki.org/xwiki/bin/view/Extension/Active%20Installs%202%20API/) with the concrete XWiki instance. Active installs assures that "there's no way to find who's having a given UUID" (referring to the instance id). Further, the information who the license owner is and information about the obtained licenses can be used for targeted phishing attacks. Also, while user information is normally public, email addresses might only be displayed obfuscated (depending on the configuration).

### Patches
This has been fixed in Application Licensing 1.24.2, by https://github.com/xwikisas/application-licensing/commit/d168fb88fc0d121bf95e769ea21c55c00bebe5a6

### Workarounds
There are no known workarounds besides upgrading.

### References
Fixed by https://github.com/xwikisas/application-licensing/commit/d168fb88fc0d121bf95e769ea21c55c00bebe5a6

## References
- https://github.com/xwikisas/application-licensing/security/advisories/GHSA-4hfp-m9gv-m753
- https://nvd.nist.gov/vuln/detail/CVE-2024-26138
- https://github.com/xwikisas/application-licensing/commit/d168fb88fc0d121bf95e769ea21c55c00bebe5a6
- https://extensions.xwiki.org/xwiki/bin/view/Extension/Active%20Installs%202%20API
- https://github.com/xwikisas/application-licensing
