# [M] Slippers Vulnerable to Cross-Site Scripting (XSS) in `attrs` Template Tag

## Summary
Severity: Medium
Advisory: GHSA-w7rv-gfp4-j9j3
CVE: CVE-2026-34231
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-w7rv-gfp4-j9j3
Type: github-advisory

## Affected
- PyPI: `slippers` — affected >=0 <0.6.3

## Details
## Summary

A Cross-site Scripting (XSS) vulnerability exists in the `{% attrs %}` template tag of the `slippers` Django package. When a context variable containing untrusted data is passed to `{% attrs %}`, the value is interpolated into an HTML attribute string without escaping, allowing an attacker to break out of the attribute context and inject arbitrary HTML or JavaScript into the rendered page.

## Vulnerability details

### Root cause

`AttrsNode` is a custom `Node` subclass registered via `register.tag()`. Unlike `register.simple_tag()`, which automatically applies `conditional_escape()` when autoescape is on, custom `Node.render()` methods receive no automatic escaping and are fully responsible for sanitising their output. `attr_string()` fails to do this:

```python
def attr_string(key: str, value: Any):
    if isinstance(value, bool):
        return key if value else ""
    key = key.replace("_", "-")
    return f'{key}="{value}"'   # value is not escaped
```

### Attack scenario

Given a template that uses `{% attrs %}` with a user-supplied value:

```django
{% load slippers %}
<input {% attrs type placeholder %}>
```

```python
render(request, "search.html", {"placeholder": request.GET.get("q", "")})
```

An attacker crafting a request with `q=" onmouseover="alert(document.cookie)" x="` produces:

```html
<input type="text" placeholder="" onmouseover="alert(document.cookie)" x="">
```

## Impact

Any template that passes values derived from user input, database content, or other untrusted sources to `{% attrs %}` is vulnerable. Successful exploitation can lead to session hijacking, credential theft, arbitrary actions on behalf of the victim, and page defacement.

## Remediation

Replace the f-string in `attr_string()` with `format_html()`, which escapes both key and value:

```python
from django.utils.html import format_html

def attr_string(key: str, value: Any):
    if isinstance(value, bool):
        return key if value else ""
    key = key.replace("_", "-")
    return format_html('{}="{}"', key, value)
```

Until a patch is available, sanitise untrusted values before passing them to `{% attrs %}`, for example with `django.utils.html.escape()` in the view layer.

## References
- https://github.com/mixxorz/slippers/security/advisories/GHSA-w7rv-gfp4-j9j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34231
- https://github.com/mixxorz/slippers/commit/16cc4ef4fa8ad2f7aee30798f16c3e7b653423b2
- https://github.com/mixxorz/slippers
- https://github.com/mixxorz/slippers/releases/tag/0.6.3
