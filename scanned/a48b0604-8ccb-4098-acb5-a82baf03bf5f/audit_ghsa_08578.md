# [M] Wagtail has improper permission handling when deleting form submissions

## Summary
Severity: Medium
Advisory: GHSA-pwm3-7fv4-g6xx
CVE: CVE-2026-44199
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-pwm3-7fv4-g6xx
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.7
- PyPI: `wagtail` — affected >=7.1 <7.3.2

## Details
### Impact

A CMS user with limited access to form pages could delete submissions to form pages they don't have access to by crafting a form submission to delete submissions on a page they do have access to for submissions they don't. 

The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches

Patched versions have been released as Wagtail 7.0.7 and 7.3.2. The new 7.4 LTS feature release also incorporates this fix.

### Workarounds

No workaround is available.


### Acknowledgements

Wagtail thanks Vishal Shukla @shukla304 for reporting this issue.

### For more information
If there are any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Send an email to [security@wagtail.org](mailto:security@wagtail.org) (view the [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-pwm3-7fv4-g6xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44199
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-148.yaml
- https://github.com/wagtail/wagtail
