# [M] Wagtail: Denial of service via unbounded filter specs in the image preview

## Summary
Severity: Medium
Advisory: GHSA-f2p5-j6fg-5cxf
CVE: CVE-2026-54260
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-f2p5-j6fg-5cxf
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.8
- PyPI: `wagtail` — affected >=7.1 <7.3.3
- PyPI: `wagtail` — affected >=7.4 <7.4.2

## Details
### Impact

An authenticated admin user can trigger expensive rendition processing with purposefully crafted filter specs resulting in potentially service degradation.

The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 7.0.8, 7.3.3, 7.4.2.

### Workarounds
For sites that cannot easily upgrade to a current supported version, the vulnerability can be patched by adding the following code to `urls.py` URL pattern declarations to override the vulnerable view.

```python
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.images.exceptions import InvalidFilterSpecError
from wagtail.images.permissions import permission_policy
from wagtail.images.views import preview


def patched_preview(request, image_id, filter_spec):
    image = get_object_or_404(get_image_model(), id=image_id)

    if not permission_policy.user_has_permission_for_instance(request.user, "change", image):
        raise PermissionDenied

    try:
        filter_obj = Filter(spec=filter_spec)
    except InvalidFilterSpecError:
        return HttpResponseBadRequest("Invalid filter spec", content_type="text/plain")

    allowed = {"original", "width", "height", "min", "max", "fill"}
    if any(operation.method not in allowed for operation in filter_obj.operations):
        return HttpResponseBadRequest("Invalid filter spec", content_type="text/plain")

    return preview(request, image_id, filter_spec)


urlpatterns = [
    # Example where the CMS admin is at /admin/.
    # Add this before the Wagtail admin URLs registration, with the same sub-path.
    path("admin/images/<int:image_id>/preview/<str:filter_spec>/", patched_preview)
    path("admin/", include(wagtailadmin_urls)),
]
```

### Acknowledgements
Many thanks to @0x1saac for reporting this issue.


### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-f2p5-j6fg-5cxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54260
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2026-613.yaml
- https://github.com/wagtail/wagtail
