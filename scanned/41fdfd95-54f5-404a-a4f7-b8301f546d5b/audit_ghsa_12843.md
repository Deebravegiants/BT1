# [M] django-ucamlookup Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pjx4-3f3p-29v3
CVE: CVE-2016-15010
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-pjx4-3f3p-29v3
Type: github-advisory

## Affected
- PyPI: `django-ucamlookup` — affected >=0 <1.9.2

## Details
A vulnerability classified as problematic was found in University of Cambridge django-ucamlookup up to 1.9.1. Affected by this vulnerability is an unknown functionality of the component Lookup Handler. The manipulation leads to cross site scripting. The attack can be launched remotely. Upgrading to version 1.9.2 can address this issue. The name of the patch is 5e25e4765637ea4b9e0bf5fcd5e9a922abee7eb3. It is recommended to upgrade the affected component. The identifier VDB-217441 was assigned to this vulnerability.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15010
- https://github.com/uisautomation/django-ucamlookup/commit/5e25e4765637ea4b9e0bf5fcd5e9a922abee7eb3
- https://github.com/pypa/advisory-database/tree/main/vulns/django-ucamlookup/PYSEC-2023-14.yaml
- https://github.com/uisautomation/django-ucamlookup
- https://github.com/uisautomation/django-ucamlookup/releases/tag/1.9.2
- https://vuldb.com/?ctiid.217441
- https://vuldb.com/?id.217441
