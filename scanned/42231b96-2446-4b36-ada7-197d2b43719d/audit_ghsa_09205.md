# [M] Grav CMS vulnerable to stored XSS via Markdown media attribute() action

## Summary
Severity: Medium
Advisory: GHSA-r7fx-8g49-7hhr
CVE: CVE-2026-42841
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-r7fx-8g49-7hhr
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
### Summary

An authenticated user with page editing permissions can inject an executable JavaScript event-handler attribute into rendered image HTML through Grav's Markdown media action syntax.

The issue is caused by Markdown image query parameters being converted into callable media actions. The public `attribute()` media method can be reached this way, allowing an editor to set an arbitrary HTML attribute name and value on the generated image element.

For example, this Markdown:

```markdown
![Quarterly market overview](market-overview.gif?attribute=onload,alert(document.domain))
```

is rendered as an image tag containing an executable `onload` handler:

```html
<img onload="alert(document.domain)" alt="Quarterly market overview" src="/user/pages/03.campaigns/market-overview.gif?...">
```

This results in stored XSS when another user views the affected page. In a multi-user Grav installation, a lower-privileged page editor could use this to target administrators or reviewers who preview or view editor-controlled content.

Tested versions:

- Grav CMS: 1.7.49.5
- Admin Plugin: 1.10.49.1

Suggested classification:

- CWE-79: Improper Neutralization of Input During Web Page Generation
- Stored Cross-Site Scripting
- Suggested CVSS v4.0 score if page editing is considered high privilege: 6.9 Medium
- Suggested CVSS v4.0 vector: `CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N`
- Suggested CVSS v3.1 score if page editing is considered high privilege: 6.9 Medium
- Suggested CVSS v3.1 vector: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N`

### Details

The issue appears to come from this source-to-sink flow:

1. `ParsedownGravTrait::inlineImage()` processes Markdown images.
2. `Excerpts::processImageExcerpt()` resolves the referenced media object.
3. `Excerpts::processMediaActions()` parses the image URL query string into media actions.
4. `call_user_func_array()` invokes the requested action method on the media object.
5. `MediaObjectTrait::attribute()` stores the attacker-controlled attribute name and value.
6. The media object returns a Parsedown element containing the injected attribute.
7. Parsedown renders the attribute name into the final HTML.

Relevant code paths:

```text
system/src/Grav/Common/Markdown/ParsedownGravTrait.php
system/src/Grav/Common/Page/Markdown/Excerpts.php
system/src/Grav/Common/Media/Traits/MediaObjectTrait.php
system/src/Grav/Common/Page/Medium/StaticImageMedium.php
system/src/Grav/Common/Page/Medium/ImageMedium.php
vendor/erusev/parsedown/Parsedown.php
```

In `system/src/Grav/Common/Markdown/ParsedownGravTrait.php`, Markdown image excerpts are passed into Grav-specific media handling:

```php
if (isset($excerpt['element']['attributes']['src'])) {
    $excerpt = $this->excerpts->processImageExcerpt($excerpt);
}
```

In `system/src/Grav/Common/Page/Markdown/Excerpts.php`, query string parameters are converted into media action calls. The query parameter name becomes the method name:

```php
$carry[] = ['method' => $parts[0], 'params' => $value];
```

The requested method is later invoked dynamically:

```php
$medium = call_user_func_array([$medium, $action['method']], $args);
```

For the payload:

```text
attribute=onload,alert(document.domain)
```

the method is `attribute`, and the arguments are `onload` and `alert(document.domain)`.

In `system/src/Grav/Common/Media/Traits/MediaObjectTrait.php`, `attribute()` stores the caller-controlled attribute name directly:

```php
public function attribute($attribute = null, $value = '')
{
    if (!empty($attribute)) {
        $this->attributes[$attribute] = $value;
    }
    return $this;
}
```

The image media classes then return the collected attributes as attributes for an `img` element.

In `system/src/Grav/Common/Page/Medium/StaticImageMedium.php`:

```php
return ['name' => 'img', 'attributes' => $attributes];
```

The non-static image path in `system/src/Grav/Common/Page/Medium/ImageMedium.php` also returns image attributes in the same way.

Finally, in `vendor/erusev/parsedown/Parsedown.php`, the attribute value is escaped, but the attribute name is rendered as-is:

```php
$markup .= ' '.$name.'="'.self::escape($value).'"';
```

As a result, the attacker-controlled attribute name `onload` is emitted into the final HTML and executes as a browser event handler.

The Admin Plugin's save-time XSS detection does not appear to block this because the stored content is Markdown media syntax, not raw HTML:

```markdown
![Quarterly market overview](market-overview.gif?attribute=onload,alert(document.domain))
```

The dangerous HTML is generated later during Markdown/media rendering.

### PoC

I reproduced this on a standard Grav CMS installation with the Admin Plugin enabled.

Configuration and prerequisites:

- Grav CMS 1.7.49.5
- Admin Plugin 1.10.49.1
- Markdown processing enabled for pages
- A user account with permission to create or edit pages
- A page media file available in the edited page folder, for example `market-overview.gif`

Steps to reproduce:

1. Install Grav CMS with the Admin Plugin.
2. Log in to the Admin panel as a user who can create or edit pages.
3. Create a normal content page or edit an existing one.
4. Add or reference a page media file named `market-overview.gif`.
5. Insert the following Markdown into the page body:

   ```markdown
   ![Quarterly market overview](market-overview.gif?attribute=onload,alert(document.domain))
   ```

6. Save the page.
7. Open the rendered frontend page in a browser.
8. The JavaScript payload executes when the image loads.
9. Inspect the generated DOM. The rendered image element contains the injected `onload` attribute.

Expected result:

The Markdown media action should not be able to generate executable HTML attributes. The payload should be rejected, sanitized, or rendered without the dangerous event-handler attribute.

Actual result:

The payload is accepted and rendered as an executable image event handler:

```html
<img onload="alert(document.domain)" alt="Quarterly market overview" src="/user/pages/03.campaigns/market-overview.gif?...">
```

Screenshots:

- the stored Markdown payload in the page editor
<img width="1718" height="1013" alt="edycja" src="https://github.com/user-attachments/assets/8f5e5275-e4ef-4d5e-a2cd-44683537b909" />
- the JavaScript alert executing on the frontend page
<img width="1727" height="1002" alt="alert" src="https://github.com/user-attachments/assets/6de81228-830c-49f2-ac41-b15658a8913d" />
- browser DevTools showing the injected `onload` attribute in the rendered DOM
<img width="939" height="539" alt="inspect" src="https://github.com/user-attachments/assets/7832c42d-6f3a-4ea2-b072-b837bd3913ed" />

### Impact

This is a stored cross-site scripting vulnerability.

An authenticated user with page editing permissions can store a malicious Markdown image reference. When the affected page is rendered, the payload executes in the browser of any user who views that page.

In multi-user Grav installations, this may allow a lower-privileged editor to target administrators, reviewers, or other privileged users who preview or view editor-controlled content. Depending on the victim's privileges and deployed plugins, successful exploitation may allow JavaScript execution in the site origin, access to same-origin page data available to the victim, and same-origin actions performed as the victim.

CVSS 4.0 rationale:

- `AV:N`: the issue is exploitable through the web application.
- `AC:L`: no special race condition or complex setup is required after page editing access is obtained.
- `AT:P`: exploitation requires the malicious Markdown/media reference to be stored in page content and later rendered to a victim.
- `PR:H`: the attacker needs page editing capability.
- `UI:P`: a victim must view the affected page. The demonstrated `onload` payload executes on passive page rendering, without requiring a click or form submission by the victim.
- `VC:H/VI:L/VA:N`: confidentiality impact can be high when the victim is an administrator or reviewer; integrity impact is limited; no direct availability impact was demonstrated.
- `SC:H/SI:L/SA:N`: the injected script executes in the browser/application context and may affect subsequent same-origin interactions available to the victim.

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`5a12f9be8`](https://github.com/getgrav/grav/commit/5a12f9be8) — will ship in **2.0.0-beta.2**.

**What changed:** `MediaObjectTrait::attribute()` — the sink reached by Markdown like `![alt](img.gif?attribute=onload,alert(1))` — now gates the attribute **name** through an allowlist regex (`^[A-Za-z][A-Za-z0-9_:.\-]*$`) plus an explicit denylist of script-context names:

- any `on*` handler (case-insensitive)
- `style` (inline CSS expression risk)
- `xmlns` (XML namespace tricks)
- `srcdoc` (iframe sandbox bypass)
- `formaction` (form action override)

Invalid names are silently dropped — the attribute isn't stored, so it doesn't survive into the rendered `<img>`. `src`/`href`/`data-*`/`aria-*`/standard media attributes are unaffected.

**Files:**
- [`system/src/Grav/Common/Media/Traits/MediaObjectTrait.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Media/Traits/MediaObjectTrait.php) — new `isSafeAttributeName()` gate.
- [`tests/unit/Grav/Common/Security/MediaAttributeSecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/MediaAttributeSecurityTest.php) — 28 cases (14 dangerous-name rejections, 14 safe-name round-trips).

### Discoverers

@K-Czaplicki
@morzelowski


---

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-r7fx-8g49-7hhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42841
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
