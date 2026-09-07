# [M] django CMS: Stored XSS in edit-mode plugin exception rendering

## Summary
Severity: Medium
Advisory: GHSA-hvq6-2r72-p2x7
CVE: CVE-2026-75526
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-hvq6-2r72-p2x7
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=5.0.8 <5.0.9

## Details
## Summary

When plugin rendering fails in edit mode, django CMS renders a `cms-rendering-exception` block so editors can see that a placeholder could not be rendered. Older code built that block's heading by interpolating the exception message, placeholder/source strings, and the failing plugin's short description directly into an HTML string, then returned the placeholder output as safe markup.

If an editor could store HTML in data used by a plugin's `get_short_description()` (or in other values interpolated into the exception message), and that plugin later raised during edit-mode rendering, the payload was parsed as HTML in the staff user's browser. This is a stored XSS condition in the CMS editing context.

## Impact

The vulnerable path is only reached when placeholder rendering catches a plugin rendering exception:

```python
try:
    placeholder_content = "".join(plugin_content)
except Exception as e:
    context["exc_info"] = sys.exc_info()
    placeholder_content = self.render_exception("rendering placeholder", context, placeholder, editable)
```

`render_exception()` constructs a `message` from values that can include stored content:

- `value` - the exception message.
- `placeholder` - the placeholder string representation.
- `placeholder.source` - the source object string representation, such as page content.
- `instance.get_short_description()` - plugin-provided summary text, often derived from plugin model fields.

In the vulnerable implementation, that message was embedded directly into an HTML heading. The final placeholder content was later returned through `mark_safe`, so Django template autoescaping did not protect the heading.

`settings.DEBUG` does not mitigate the issue: it only controls whether Django's traceback HTML is appended. The custom heading is rendered in edit mode regardless of `DEBUG`.

## Patch

Escape the custom exception heading before returning it as safe placeholder markup. The current fixed code uses `format_html`, which escapes `message` before inserting it into the heading:

```python
heading = format_html('<h2 class="cms-rendering-exception-title">{}</h2>', message)
```

The traceback HTML from `ExceptionReporter.get_traceback_html()` should remain separate from django CMS's custom heading; Django's traceback escaping does not protect additional HTML assembled by django CMS.

## Workarounds

Until patched, reduce exposure by ensuring only fully trusted staff can edit plugins whose stored fields are included in `get_short_description()`, and fix or disable plugins that can be made to raise during edit-mode rendering. This is only a partial mitigation because the escaping bug is in the shared exception-rendering path.

## References

- `cms/plugin_rendering.py` - `ContentRenderer.render_placeholder`
- `cms/plugin_rendering.py` - `ContentRenderer.render_exception`
- Fixed code: `heading = format_html('<h2 class="cms-rendering-exception-title">{}</h2>', message)`
- Regression tests:
  `cms.tests.test_plugin_renderers.TestExceptionCatchers.test_exception_in_plugin_render_escapes_user_content_in_edit_mode`,
  `cms.tests.test_plugin_renderers.TestLegacyRendererExceptionCatcher.test_exception_in_plugin_render_escapes_user_content_in_edit_mode`

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-hvq6-2r72-p2x7
- https://github.com/django-cms/django-cms/pull/8711
- https://github.com/django-cms/django-cms/commit/b56a568844ff3702495945f73a31d0868285bf88
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.9
