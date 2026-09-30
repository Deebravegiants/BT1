# [M] django CMS: Missing authorization in `render_object_structure` discloses non-PageContent placeholder structure to low-privileged staff

## Summary
Severity: Medium
Advisory: GHSA-8qj2-c6q4-f399
CVE: CVE-2026-61663
CWE: CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8qj2-c6q4-f399
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <5.0.9

## Details
## Summary

The django-cms frontend-editing structure endpoint

```
GET /<lang>/admin/cms/placeholder/object/<content_type_id>/structure/<object_id>/
```

did not perform an object-level authorization check for **non-`PageContent`** objects. Any authenticated, active staff user could request the structure endpoint for a frontend-editable object (a model using `PlaceholderRelationField`) and read its placeholder/plugin structure, even without permission to change that object and without the `cms.use_structure` permission that the toolbar UI requires before offering structure mode.

`PageContent` objects were already protected (a page-view check added in GHSA/PR #8644); this advisory covers the remaining non-`PageContent` branch of the same view.

## Severity

The issue is staff-gated and read-only, disclosing CMS structure metadata (placeholder slot names, plugin tree, plugin identifiers/labels, object existence) rather than write access or arbitrary field data.

## Affected versions

- django-cms `>= 4.0.0, <= 5.0.x` and `5.1.0a1`
  (the vulnerable non-`PageContent` branch was introduced with the frontend-editing endpoints in 4.0)

## Patched versions

- django-cms TODO: 5.0.9

## Preconditions

- An authenticated, active staff account (`is_staff=True`).
- The deployment exposes a non-`PageContent` model with django-cms placeholders / frontend editing (e.g. via `PlaceholderRelationField`).
- The attacker can guess or enumerate the target `content_type_id` and object id.
- The attacker needs **no** model/object change permission and **no** `cms.use_structure` permission.

## Impact

A low-privileged staff user can read the editorial placeholder/plugin structure of non-`PageContent` objects they are not authorized to edit through the toolbar. Depending on the installed plugins and templates this may reveal placeholder names, plugin layout, plugin identifiers and the existence of objects owned by other staff users or teams. This is most relevant for deployments using third-party or custom django-cms apps that expose frontend-editable objects outside the page tree.

## Proof of concept

Using django-cms' own test model `placeholder_relation_field_app.FancyPoll` (a non-`PageContent` model with a `PlaceholderRelationField`):

```python
target = FancyPoll.objects.create(name="private-fancy-poll")
placeholder = rescan_placeholders_for_obj(target)["content"]
attacker = self._create_user("low_staff", is_staff=True, is_superuser=False)
# attacker has neither change_fancypoll nor cms.use_structure

with self.login_user_context(attacker):
    response = self.client.get(get_object_structure_url(target, language="en"))

# Before fix: HTTP 200, body contains '"placeholder_id": "<pk>"'
# After fix:  HTTP 404, structure not disclosed
```

## Patch

`render_object_structure` now authorizes the non-`PageContent` branch, mirroring
`Placeholder.has_change_permission` at the object level (honouring a custom
`has_placeholder_change_permission` hook, otherwise falling back to the model/object
change permission) and returning `404` when the user is not authorized:

```python
else:
    content_type_obj = content_type.get_object_for_this_type(pk=object_id)
    if not _can_change_placeholder_object(request.user, content_type_obj):
        raise Http404
```

## Workarounds

No configuration workaround. Deployments that do not register any non-`PageContent`
frontend-editable model are not affected. Otherwise, upgrade to a patched release.

## Credit

Reported by **doanmanhducz**.

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-8qj2-c6q4-f399
- https://github.com/django-cms/django-cms/pull/8703
- https://github.com/django-cms/django-cms/commit/9c82abfeb25471583e23906ea1ebef9202527b04
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.9
