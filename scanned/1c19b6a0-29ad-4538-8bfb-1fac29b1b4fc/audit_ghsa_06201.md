# [M] Wagtail: Pages translations can be created without page permissions when using simple_translation

## Summary
Severity: Medium
Advisory: GHSA-8634-mr4j-r72c
CVE: CVE-2026-54262
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8634-mr4j-r72c
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.8
- PyPI: `wagtail` — affected >=7.1 <7.3.3
- PyPI: `wagtail` — affected >=7.4 <7.4.2

## Details
### Impact
A low-level user with the "Can submit translation" permission can create translations for any page, including those they do not have permissions for.

### Patches
Patched versions have been released as Wagtail 7.0.8, 7.3.3, 7.4.2.

### Workarounds
N/A

### Acknowledgements

Many thanks to @devansh3008 and @alanturing881 for reporting this issue.

### For more information

If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-8634-mr4j-r72c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54262
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-615.yaml
- https://github.com/wagtail/wagtail
