# [M] Wagtail has improper permission handling on admin preview endpoints

## Summary
Severity: Medium
Advisory: GHSA-4qvv-g3vr-m348
CVE: CVE-2026-25517
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-4qvv-g3vr-m348
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <6.3.6
- PyPI: `wagtail` — affected >=6.4rc1 <7.0.4
- PyPI: `wagtail` — affected >=7.1rc1 <7.1.3
- PyPI: `wagtail` — affected >=7.2rc1 <7.2.2
- PyPI: `wagtail` — affected >=7.3rc1 <7.3

## Details
### Impact
Due to a missing permission check on the preview endpoints, a user with access to the Wagtail admin and knowledge of a model's fields can craft a form submission to obtain a preview rendering of any page, snippet or site setting object for which previews are enabled, consisting of any data of the user's choosing. The existing data of the object itself is not exposed, but depending on the nature of the template being rendered, this may expose other database contents that would otherwise only be accessible to users with edit access over the model. The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 6.3.6, 7.0.4, 7.1.3 and 7.2.2. The new 7.3 feature release also incorporates this fix.

### Workarounds
No workaround is available.

### Acknowledgements

Many thanks to @thxtech for reporting this issue.

### For more information

If there are any questions or comments about this advisory:

- Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
- Send an email to [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-4qvv-g3vr-m348
- https://nvd.nist.gov/vuln/detail/CVE-2026-25517
- https://github.com/wagtail/wagtail/commit/01fd3477365a193e6a8270311defb76e890d2719
- https://github.com/wagtail/wagtail/commit/5f09b6da61e779b0e8499bdbba52bf2f7bd3241f
- https://github.com/wagtail/wagtail/commit/73f070dbefbd3b39ea6649ce36bd2d2a6eef2190
- https://github.com/wagtail/wagtail/commit/7dfe8de5f8b3f112c73c87b6729197db16454915
- https://github.com/wagtail/wagtail/commit/dd824023a031f1b82a6b6f83a97a5c73391b7c03
- https://github.com/wagtail/wagtail
- https://github.com/wagtail/wagtail/releases/tag/v6.3.6
- https://github.com/wagtail/wagtail/releases/tag/v7.0.4
- https://github.com/wagtail/wagtail/releases/tag/v7.1.3
- https://github.com/wagtail/wagtail/releases/tag/v7.2.2
- https://github.com/wagtail/wagtail/releases/tag/v7.3
