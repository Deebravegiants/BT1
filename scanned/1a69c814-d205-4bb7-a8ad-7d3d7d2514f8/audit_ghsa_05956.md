# [M] django CMS: Broken access control in page *Duplicate* allows reading the content of any page (cross-site / restriction bypass)

## Summary
Severity: Medium
Advisory: GHSA-6x92-6vx4-5fwr
CVE: CVE-2026-63003
CWE: CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-6x92-6vx4-5fwr
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <5.0.9

## Details
## Impact

The only authorization gate on the duplicate flow is `PageAdmin.has_add_permission`,
which checks `user_can_add_page(user, site)` / `user_can_add_subpage(...)` — i.e. *“may
this user create a page at all”*. Nothing checks the user’s relationship to the page being
copied:

- `cms/admin/forms.py` — `DuplicatePageForm.source = ModelChoiceField(queryset=Page.objects.all(), widget=HiddenInput())`
  spans **every page in the database, on every site**.
- `cms/admin/forms.py` — `AddPageForm.__init__` returns early when the `source` widget is
  hidden, so the queryset is **never narrowed** to the user’s site/subtree.
- `cms/admin/forms.py` — `AddPageForm.clean()` validates only URL uniqueness; `source` is
  never validated against the user.
- `cms/admin/pageadmin.py` — `duplicate()` seeds `source` from the URL **only on GET**; on
  POST the value comes entirely from the request body.
- `cms/admin/forms.py` — `AddPageForm.save()` → `from_source()` performs
  `source.copy(..., permissions=False)` and copies **every placeholder and all plugins** of
  `source` into a new page on the attacker’s site. Because `permissions=False` drops the
  source’s view restrictions, the resulting copy is fully readable by the attacker.

This crosses a real privilege boundary: a staff user restricted (via `CMS_PERMISSION`) to
their own site or subtree can exfiltrate the content of restricted pages and of pages
belonging to other tenants.

**Read-back is trivial (verified):** the copy is created on the attacker’s site and, because
`copy(..., permissions=False)` strips the source’s view restrictions, the new page is
*unrestricted*. `user_can_view_page()` then returns `True` for it (unrestricted +
`PUBLIC_FOR`), so the attacker — or even an anonymous visitor — can read the duplicated
content directly from the front end. No further permission on the new page is required.

## Proof of concept

1. Log in as a staff user `attacker` who has *add page* permission but **no** view/change
   permission on a target (secret / other-site) page `SECRET_ID`.
2. Send (the URL `<id>` only needs to be a `PageContent` the attacker can already see —
   e.g. one of their own pages; the victim id goes in the POST body):

```http
POST /admin/cms/pagecontent/<MY_OWN_PAGECONTENT_ID>/duplicate/ HTTP/1.1
Cookie: sessionid=<attacker session>
Content-Type: application/x-www-form-urlencoded

csrfmiddlewaretoken=...&title=x&slug=x&language=en&source=<SECRET_ID>
```

3. A new, unrestricted page is created under the attacker’s site containing a verbatim
   copy of the secret page’s plugins, which the attacker can now preview/edit/read.

## Patches 

Enforce an object-level permission check on `source`:

```python
class DuplicatePageForm(AddPageForm):
    source = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        required=True,
        widget=forms.HiddenInput(),
    )

    def clean_source(self):
        source = self.cleaned_data.get("source")
        if source and not user_can_view_page(self._user, source):
            raise ValidationError(_("You do not have permission to copy this page."))
        return source
```

(`user_can_view_page` is imported from `cms.utils.page_permissions`.)

## Workarounds

Until patched, restrict access to the `cms.add_page` permission to fully-trusted staff, or
disable the duplicate action for delegated/limited editors.

## References

- `cms/admin/pageadmin.py` — `duplicate()`, `has_add_permission()`, `get_urls()`
- `cms/admin/forms.py` — `DuplicatePageForm`, `AddPageForm.__init__/clean/save/from_source`
- Regression tests: `cms/tests/test_forms.py::DuplicatePageFormSecurityTestCase`

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-6x92-6vx4-5fwr
- https://github.com/django-cms/django-cms/pull/8713
- https://github.com/django-cms/django-cms/commit/3e1ccf7573eb1a74ebbbfaaa812c1f5cadf14e6c
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.9
