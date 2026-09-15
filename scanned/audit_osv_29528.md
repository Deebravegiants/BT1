# [H] openedx-translations's Atlas translations for Open edX missing validation

## Summary
Severity: High
Advisory: CVE-2024-43782
Aliases: GHSA-fg8c-2pvj-wx3j
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2024-08-23
Source: https://osv.dev/vulnerability/CVE-2024-43782
Type: osv

## Details
This openedx-translations repository contains translation files from Open edX repositories to be kept in sync with Transifex. Before moving to pulling translations from the openedx-translations repository via openedx-atlas, translations in the edx-platform repository were validated using edx-i18n-tools. This validation included protection against malformed translations and translations-based script injections. Prior to this patch, the validation implemented in the openedx-translations repository did not include the same protections. The maintainer inspected the translations in the edx-platform directory of both the main and open-release/redwood.master branches of the openedx-translations repository and found no evidence of exploited translation strings.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43782.json
- https://github.com/openedx/openedx-translations/security/advisories/GHSA-fg8c-2pvj-wx3j
- https://nvd.nist.gov/vuln/detail/CVE-2024-43782
- https://github.com/openedx/openedx-translations/commit/3c4093705dec99590577c4d8270ce263f7fffc5a
- https://github.com/openedx/openedx-translations/commit/b2444340e8702c7955310331c1db5fd85b25b92b
