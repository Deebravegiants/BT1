# [M] Possible XSS attack in Wagtail

## Summary
Severity: Medium
Advisory: GHSA-v2wc-pfq2-5cm6
CVE: CVE-2020-11001
CWE: CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-14
Source: https://github.com/advisories/GHSA-v2wc-pfq2-5cm6
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=1.9.0 <2.7.2
- PyPI: `wagtail` — affected >=2.8.0 <2.8.1

## Details
### Impact
A cross-site scripting (XSS) vulnerability exists on the page revision comparison view within the Wagtail admin interface. A user with a limited-permission editor account for the Wagtail admin could potentially craft a page revision history that, when viewed by a user with higher privileges, could perform actions with that user's credentials. The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 2.7.2 (for the LTS 2.7 branch) and Wagtail 2.8.1 (for the current 2.8 branch).

### Workarounds
Site owners who are unable to upgrade to the new versions can disable the revision comparison view by adding the following URL route to the top of their project's `urls.py` configuration:

    from django.views.generic.base import RedirectView

    urlpatterns = [
        url(r'^admin/pages/(\d+)/revisions/compare/', RedirectView.as_view(url='/admin/')),
        # ...
    ]

### Acknowledgements
Many thanks to Vlad Gerasimenko for reporting this issue.

### For more information
If you have any questions or comments about this advisory:
* Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
* Email us at [security@wagtail.io](mailto:security@wagtail.io) (if you wish to send encrypted email, the public key ID is `0x6ba1e1a86e0f8ce8`)

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-v2wc-pfq2-5cm6
- https://nvd.nist.gov/vuln/detail/CVE-2020-11001
- https://github.com/wagtail/wagtail/commit/61045ceefea114c40ac4b680af58990dbe732389
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2020-152.yaml
- https://github.com/wagtail/wagtail/releases/tag/v2.8.1
