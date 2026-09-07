# [M] Wagtail has improper permission handling when copying pages

## Summary
Severity: Medium
Advisory: GHSA-67rv-mg8q-5pf3
CVE: CVE-2026-44200
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-67rv-mg8q-5pf3
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.7
- PyPI: `wagtail` — affected >=7.1 <7.3.2

## Details
### Impact

A CMS user with limited access to pages could copy a page they don't have access to to an area of the site they do. Once copied, they'd be able to view its contents, and potentially publish it. Permissions were correctly checked for the copy destination, but not for the source page.

### Patches

Patched versions have been released as Wagtail 7.0.7 and 7.3.2. The new 7.4 LTS feature release also incorporates this fix.

### Workarounds

No workaround is available.


### Acknowledgements

Wagtail thanks independent security researcher Sanjok Karki @thesanjok for reporting this issue.

### For more information
If there are any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Send an email to [security@wagtail.org](mailto:security@wagtail.org) (view the [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-67rv-mg8q-5pf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44200
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-149.yaml
- https://github.com/wagtail/wagtail
