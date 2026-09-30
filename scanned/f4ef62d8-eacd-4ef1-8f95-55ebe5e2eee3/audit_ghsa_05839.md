# [M] Wagtail: Improper restriction handling on Pages admin API

## Summary
Severity: Medium
Advisory: GHSA-3vrh-m9w7-v94f
CVE: CVE-2026-55468
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-3vrh-m9w7-v94f
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.9
- PyPI: `wagtail` — affected >=7.1 <7.3.4
- PyPI: `wagtail` — affected >=7.4 <7.4.3
- PyPI: `wagtail` — affected >=8.0rc1 <8.0rc2

## Details
### Impact

The internal Pages admin [API](https://docs.wagtail.org/en/stable/advanced_topics/api/index.html) incorrectly returns page fields  without access control when they are declared in `api_fields`. A user with access to the Wagtail admin can use this API to fetch draft and live page fields’ contents that are part of `api_fields` on the base page model (title, slug, seo_title, search_description), as well as all custom fields declared in `api_fields`.

The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches

Patched versions have been released as Wagtail 7.0.9, 7.3.4, 7.4.3 and 8.0rc2.

### Workarounds

Site owners unable to upgrade can apply the fix by overriding the relevant method on `PagesAdminAPIViewSet` to patch all vulnerable admin API endpoints:

```python
# wagtail_hooks.py or AppConfig.ready()

from wagtail.admin.api.views import PagesAdminAPIViewSet
from wagtail.permissions import page_permission_policy


def _restricted_get_base_queryset(self):
    return page_permission_policy.explorable_instances(self.request.user)

PagesAdminAPIViewSet.get_base_queryset = _restricted_get_base_queryset
```

### Acknowledgements

Many thanks to xuliang@QAX for reporting this issue.

### For more information

If you have any questions or comments about this advisory:

-   Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
-   Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-3vrh-m9w7-v94f
- https://github.com/wagtail/wagtail
