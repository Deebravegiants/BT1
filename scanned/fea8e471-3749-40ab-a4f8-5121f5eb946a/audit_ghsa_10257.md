# [M] wger has Stored XSS via Unescaped License Attribution Fields

## Summary
Severity: Medium
Advisory: GHSA-6f54-qjvm-wwq3
CVE: CVE-2026-40353
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-6f54-qjvm-wwq3
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
# Stored XSS via Unescaped License Attribution Fields

## Summary

The `AbstractLicenseModel.attribution_link` property in `wger/utils/models.py` constructs HTML strings by directly interpolating user-controlled fields (`license_author`, `license_title`, `license_object_url`, `license_author_url`, `license_derivative_source_url`) without any escaping. The resulting HTML is rendered in the ingredient view template using Django's `|safe` filter, which disables auto-escaping. An authenticated user can create an ingredient with a malicious `license_author` value containing JavaScript, which executes when any user (including unauthenticated visitors) views the ingredient page.

## Severity

**High** (CVSS 3.1: ~7.6)

- Low-privilege attacker (any authenticated non-temporary user)
- Stored XSS — persists in database
- Triggers on a public page (no authentication needed to view)
- Can steal session cookies, perform actions as other users, redirect to phishing

## CWE

CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')

## Affected Components

### Vulnerable Property
**File:** `wger/utils/models.py:88-110`

```python
@property
def attribution_link(self):
    out = ''
    if self.license_object_url:
        out += f'<a href="{self.license_object_url}">{self.license_title}</a>'
    else:
        out += self.license_title  # NO ESCAPING
    out += ' by '
    if self.license_author_url:
        out += f'<a href="{self.license_author_url}">{self.license_author}</a>'
    else:
        out += self.license_author  # NO ESCAPING
    out += f' is licensed under <a href="{self.license.url}">{self.license.short_name}</a>'
    if self.license_derivative_source_url:
        out += (
            f'/ A derivative work from <a href="{self.license_derivative_source_url}">the '
            f'original work</a>'
        )
    return out
```

### Unsafe Template Rendering
**File:** `wger/nutrition/templates/ingredient/view.html`

- **Line 171:** `{{ ingredient.attribution_link|safe }}`
- **Line 226:** `{{ image.attribution_link|safe }}`

### Writable Entry Point
**File:** `wger/nutrition/views/ingredient.py:154-175`

```python
class IngredientCreateView(WgerFormMixin, CreateView):
    model = Ingredient
    form_class = IngredientForm  # includes license_author field
```

**URL:** `login_required(ingredient.IngredientCreateView.as_view())` — any authenticated non-temporary user.

**Form fields (from `wger/nutrition/forms.py:295-313`):** includes `license_author` (TextField, max_length=3500) — no sanitization.

### Models Affected

6 models inherit from `AbstractLicenseModel`:
- `Exercise`, `ExerciseImage`, `ExerciseVideo`, `Translation` (exercises module)
- `Ingredient`, `Image` (nutrition module)

Only the **Ingredient** and nutrition **Image** models' attribution links are currently rendered with `|safe` in templates.

## Root Cause

1. `attribution_link` constructs raw HTML by string interpolation of user-controlled fields without calling `django.utils.html.escape()` or `django.utils.html.format_html()`
2. The template renders the result with `|safe`, bypassing Django's auto-escaping
3. The `license_author` field in `IngredientForm` has no input sanitization
4. The `set_author()` method only sets a default value if the field is empty — it does not sanitize user-provided values

## Reproduction Steps (Verified)

### Prerequisites
- A wger instance with user registration enabled (default)
- An authenticated user account (non-temporary)

### Steps

1. **Register/login** to a wger instance

2. **Create a malicious ingredient** via the web form at `/en/nutrition/ingredient/add/`:
   - Set `Name` to any valid name (e.g., "XSS Form Verified")
   - Set `Energy` to `125`, `Protein` to `10`, `Carbohydrates` to `10`, `Fat` to `5` (energy must approximately match macros)
   - Set `Author(s)` (license_author) to:
     ```
     <img src=x onerror="alert(document.cookie)">
     ```
   - Submit the form — **the form validates and saves successfully with no sanitization**

3. **View the ingredient page** (public URL, no auth needed):
   - Navigate to the newly created ingredient's detail page
   - The XSS payload executes in the browser

### Verified PoC Output

The rendered HTML in the ingredient detail page (line 171 of `ingredient/view.html`) contains:

```html
<small>
     by <img src=x onerror=alert(1)> is licensed under <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.en">CC-BY-SA 3</a>
</small>
```

The `<img>` tag with `onerror` handler is injected directly into the page DOM and executes JavaScript when the browser attempts to load the non-existent image.

### Alternative API Path (ExerciseImage)

For users who are "trustworthy" (account >3 weeks old + verified email):

```bash
# Upload exercise image with XSS in license_author
curl -X POST https://wger.example.com/api/v2/exerciseimage/ \
  -H "Authorization: Token <token>" \
  -F "exercise=1" \
  -F "image=@photo.jpg" \
  -F 'license_author=<img src=x onerror="alert(document.cookie)">' \
  -F "license=2"
```

Note: ExerciseImage's `attribution_link` is not currently rendered with `|safe` in exercise templates, but the data is stored with XSS payloads and would execute if any template renders it with `|safe` in the future. The API serializer also returns the unescaped `attribution_link` data, which could cause XSS in API consumers (mobile apps, SPAs).

## Impact

- **Session hijacking**: Steal admin session cookies to gain full control
- **Account takeover**: Modify other users' passwords or email addresses
- **Data theft**: Access other users' workout plans, nutrition data, and personal measurements
- **Worm-like propagation**: Malicious ingredient could inject XSS that creates more malicious ingredients
- **Phishing**: Redirect users to fake login pages

## Suggested Fix

Replace the `attribution_link` property with properly escaped HTML using Django's `format_html()`:

```python
from django.utils.html import format_html, escape

@property
def attribution_link(self):
    parts = []

    if self.license_object_url:
        parts.append(format_html('<a href="{}">{}</a>', self.license_object_url, self.license_title))
    else:
        parts.append(escape(self.license_title))

    parts.append(' by ')

    if self.license_author_url:
        parts.append(format_html('<a href="{}">{}</a>', self.license_author_url, self.license_author))
    else:
        parts.append(escape(self.license_author))

    parts.append(format_html(
        ' is licensed under <a href="{}">{}</a>',
        self.license.url, self.license.short_name
    ))

    if self.license_derivative_source_url:
        parts.append(format_html(
            '/ A derivative work from <a href="{}">the original work</a>',
            self.license_derivative_source_url
        ))

    return mark_safe(''.join(str(p) for p in parts))
```

Alternatively, remove the `|safe` filter from the templates and escape in the property, though this would break the anchor tags.

## References

- [Django Security: Cross Site Scripting (XSS) protection](https://docs.djangoproject.com/en/5.0/topics/security/#cross-site-scripting-xss-protection)
- [Django `format_html()` documentation](https://docs.djangoproject.com/en/5.0/ref/utils/#django.utils.html.format_html)
- [OWASP: Stored Cross-Site Scripting](https://owasp.org/www-community/attacks/xss/#stored-xss-attacks)

## References
- https://github.com/wger-project/wger/security/advisories/GHSA-6f54-qjvm-wwq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40353
- https://github.com/wger-project/wger
- https://github.com/wger-project/wger/releases/tag/2.5
