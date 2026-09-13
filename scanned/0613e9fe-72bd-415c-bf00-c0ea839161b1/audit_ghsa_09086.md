# [M] Grav Vulnerable to XSS via Taxonomy Field Values in Admin Panel

## Summary
Severity: Medium
Advisory: GHSA-c2q3-p4jr-c55f
CVE: CVE-2026-42842
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-c2q3-p4jr-c55f
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
### Summary

A Stored Cross-Site Scripting (XSS) vulnerability exists in the Grav CMS Form plugin's select field template. Taxonomy tag and category values are rendered with the Twig `|raw` filter in the admin panel, bypassing the global autoescape protection. An editor-level user can inject arbitrary JavaScript that executes in any administrator's browser session when they view or edit any page in the admin panel.

Additionally, Grav's built-in XSS detection (`Security::detectXss()`) can be bypassed by using payloads that close the `<option>/<select>` context and use unquoted event handlers - the `on_events` regex fails to match event handlers without quotes or trailing spaces before `>`.

### Important

- The vulnerability is in the Form plugin (`select.html.twig`), which is installed by default with Grav
- The XSS is cross-page: a malicious taxonomy value on one page executes when an admin edits any page, because taxonomy options are rendered from a shared global pool
- An editor can exploit this without any other vulnerability - taxonomy fields are not in the server-side restricted fields list
- The `HttpOnly` flag on session cookies prevents direct session theft, but the XSS can steal the admin nonce and perform privileged actions via JavaScript

### Permissions Needed

- Editor: can create or edit pages and set taxonomy tag/category values

### Details

The Form plugin's select field template renders option values using the `|raw` Twig filter, which outputs content without HTML escaping:

File: `user/plugins/form/templates/forms/fields/select/select.html.twig`

```twig
{# Line 55 #}
 avalue|raw 

{# Line 65 #}
 suboption|t|raw 

{# Line 72 #}
 item_value|t|raw 
```

The taxonomy field in the page editor uses this select template. When a page has taxonomy values (tags, categories), these values are populated as `<option>` elements in the select dropdown. The `value` attribute is properly escaped by the browser's attribute encoding, but the **display text** between `<option>` tags is rendered raw:

```html
<option value="&lt;script&gt;alert(1)&lt;/script&gt;"><script>alert(1)</script></option>
```

Since taxonomy options are collected globally across all pages (to provide autocomplete/selection), a malicious taxonomy value on any page will appear in the taxonomy dropdown of every page editor - making this a cross-page stored XSS.

The server-side field restriction in the flex-objects plugin only blocks `['form', 'forms', 'process', 'twig']` for non-super users. Taxonomy fields are not restricted, so editors can freely set arbitrary taxonomy values.

### XSS Detection Bypass

Grav's `Security::detectXss()` checks for `dangerous_tags` (e.g., `<script>`, `<iframe>`), `on_events` (event handlers), and `invalid_protocols` (e.g., `javascript:`). However, the `on_events` regex:

```php
'on_events' => '#(<[^>]+[a-z\x00-\x20"\'\/)(?:on[a-z]+)\s*=[\s|\'"'].*[\s|\'"']>#iUu'
```

requires either quotes around the handler value or a trailing space before `>`. An unquoted handler like `onerror=alert(1)>` (no space before `>`) bypasses this check entirely.

Combined with `</option></select>` to break out of the select context (neither tag is in `dangerous_tags`), the full payload evades all three detection layers and triggers no XSS warning in the admin panel.

### PoC

#### Step 1: Login as Editor
Navigate to `http://TARGET/admin/` and authenticate with editor credentials.

#### Step 2: Create a Page with Malicious Taxonomy
- Go to Pages → Add → Add Page
- Title: `XSS via editor`
- Go to **Options** Tap
- On Taxonomies, Add tag:
```
</option></select><img src=x onerror=alert('XSS-via-editor')>
```

This payload:
- Closes `</option></select>` to break out of the select dropdown context
- Injects an `<img>` tag with an unquoted `onerror` handler (bypasses `on_events` regex)
- Is not in the `dangerous_tags` list (no `<script>`, `<iframe>`, etc.)
- Triggers no XSS warning in the admin panel

<img width="1221" height="857" alt="image" src="https://github.com/user-attachments/assets/6223cbb2-f04b-46bd-89ce-828c89ad77ab" />

#### Step 3: Trigger the XSS
When any administrator navigates to the page editor of any page (not just the malicious one), the JavaScript executes immediately.

<img width="1224" height="856" alt="image" src="https://github.com/user-attachments/assets/f008b0f2-dedb-4b22-a74a-cdc0d7325cb4" />

The XSS fires because taxonomy tag options are collected globally across all pages and rendered with `|raw` in the select dropdown template. The payload breaks out of the `<option>` context, and the browser renders the `<img>` tag as a regular DOM element.

### Impact

- Session hijacking: While `HttpOnly` prevents direct cookie theft, the XSS can steal the admin nonce token and perform any admin action via AJAX requests
- Privilege escalation: An editor can perform admin-only actions (create users, modify system configuration, install plugins) through the hijacked admin session
- Cross-page impact: A single malicious taxonomy value affects the entire admin panel - every page editor view is compromised


---

## Maintainer note — fix applied (2026-04-24)

Fixed across two repos:

1. **grav-plugin-form 9.0.1** (commit [`6bffb4c`](https://github.com/getgrav/grav-plugin-form/commit/6bffb4c)) — the primary fix. All four `|raw` filters in [`templates/forms/fields/select/select.html.twig`](https://github.com/getgrav/grav-plugin-form/blob/develop/templates/forms/fields/select/select.html.twig) (placeholder, avalue, suboption, item_value) have been removed. Option labels — including taxonomy values that propagate cross-page through the admin's shared selection pool — now go through Twig's default escaper, so a lower-privileged editor can no longer inject script that runs in an admin's browser when they open any page editor.

2. **Grav core on the `2.0` branch** (commit [`5a12f9be8`](https://github.com/getgrav/grav/commit/5a12f9be8), ships in **2.0.0-beta.2**) — closes the detection-bypass half of the report. The `on_events` regex in `Security::detectXss()` is tightened so unquoted handlers like `onerror=alert(1)>` are flagged (see separate GHSA-9695-8fr9-hw5q), and `option`/`select` have been added to default `security.xss_dangerous_tags` so `</option></select>…` tripwires the detector (see separate GHSA-w8cg-7jcj-4vv2).

Sites running admin2 on Grav 2.0.0-beta.2 get the 9.0.1 form plugin automatically via its existing dependency graph.

**Files:**
- [`templates/forms/fields/select/select.html.twig`](https://github.com/getgrav/grav-plugin-form/blob/develop/templates/forms/fields/select/select.html.twig) — four `|raw` removed.
- [`system/config/security.yaml`](https://github.com/getgrav/grav/blob/2.0/system/config/security.yaml) — dangerous-tags list extended.
- [`system/src/Grav/Common/Security.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Security.php) — `on_events` regex tightened.
- [`tests/unit/Grav/Common/Security/DetectXssTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/DetectXssTest.php) — includes the GHSA-c2q3 PoC payload.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-c2q3-p4jr-c55f
- https://nvd.nist.gov/vuln/detail/CVE-2026-42842
- https://github.com/getgrav/grav-plugin-form/commit/6bffb4c98be468a155d1656544ec45bb4a443957
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
