# [H] Wagtail: Reflected XSS in dynamic image URL generator view

## Summary
Severity: High
Advisory: GHSA-23m2-mghx-vqmf
CVE: CVE-2026-54263
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-23m2-mghx-vqmf
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=7.3 <7.3.3
- PyPI: `wagtail` — affected >=7.4 <7.4.2

## Details
### Impact

A reflected cross-site scripting (XSS) vulnerability exists on the dynamic image URL generator view within the Wagtail admin interface. A user with a limited-permission editor account for the Wagtail admin could craft a URL that, when viewed by a user with higher privileges, could perform actions with that user's credentials. The vulnerability is present for all sites, even if they do not enable the [dynamic image serve view](https://docs.wagtail.org/en/stable/advanced_topics/images/image_serve_view.html). The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches

Patched versions have been released as Wagtail 7.3.3 and 7.4.2.

### Workarounds

For sites that cannot easily upgrade to a current supported version, the vulnerability can be patched by adding the following code to `urls.py` URL pattern declarations to override the vulnerable view. This disables the admin dynamic image preview functionality, while the public-facing dynamic image serve view still works.

```python
from django.http import HttpResponseBadRequest
from django.urls import path
from wagtail.admin import urls as wagtailadmin_urls

def disabled_output(request, image_id):
    return HttpResponseBadRequest("", content_type="text/plain")

urlpatterns = [
    # Example where the CMS admin is at /admin/.
    # Add this before the Wagtail admin URLs registration, with the same sub-path.
    path("admin/images/<int:image_id>/generate_url/output/", disabled_output),
    path("admin/", include(wagtailadmin_urls)),
]
```

### Acknowledgements

Many thanks to Thibaud Colas (@thibaudcolas) for reporting this issue.

### For more information

If you have any questions or comments about this advisory:

- Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
- Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-23m2-mghx-vqmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54263
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-616.yaml
- https://github.com/wagtail/wagtail
