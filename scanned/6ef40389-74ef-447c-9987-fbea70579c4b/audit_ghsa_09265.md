# [M] Wagtail has improper permission handling when comparing revisions

## Summary
Severity: Medium
Advisory: GHSA-c6wj-9vcj-75pj
CVE: CVE-2026-44197
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-c6wj-9vcj-75pj
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.7
- PyPI: `wagtail` — affected >=7.1 <7.3.2

## Details
### Impact

A CMS user without the ability to edit a page could access revisions of the page through the revision compare view if they knew the primary key of two revisions. This could potentially result in disclosure of sensitive information.

### Patches

Patched versions have been released as Wagtail 7.0.7 and 7.3.2. The new 7.4 LTS feature release also incorporates this fix.

### Workarounds

No workaround is available.

### Acknowledgements

Many thanks to Seoyoung Kang @seoyoung-kang from AhnLab and an independent security researcher for reporting this issue.

### For more information
If there are any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Send an email to [security@wagtail.org](mailto:security@wagtail.org) (view the [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-c6wj-9vcj-75pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44197
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-146.yaml
- https://github.com/wagtail/wagtail
