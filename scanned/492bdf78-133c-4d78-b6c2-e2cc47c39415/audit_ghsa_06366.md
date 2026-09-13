# [M] Wagtail: Improper restriction handling on Documents and Images chosen endpoints

## Summary
Severity: Medium
Advisory: GHSA-h54r-xq46-qwqm
CVE: CVE-2026-54259
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-h54r-xq46-qwqm
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.8
- PyPI: `wagtail` — affected >=7.1 <7.3.3
- PyPI: `wagtail` — affected >=7.4 <7.4.2

## Details
### Impact
The Documents and Images chooser's chosen endpoint incorrectly listed items for which the user has not been granted choose permission. A user with access to the Wagtail admin could see the filename and name and URLs of documents and images in those collections.

The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 7.0.8, 7.3.3, 7.4.2.

### Workarounds
N/A

### Acknowledgements
Many thanks to @harshakshit for reporting this issue.


### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-h54r-xq46-qwqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54259
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-612.yaml
- https://github.com/wagtail/wagtail
