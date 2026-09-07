# [H] HaxCMS has a stored Cross-Site Scripting (XSS) bypass in its saveNode endpoint

## Summary
Severity: High
Advisory: GHSA-g2g8-95qg-v35h
CVE: CVE-2026-48527
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-g2g8-95qg-v35h
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <26.0.1

## Details
## Summary

HaxCMS is affected by a stored cross-site scripting (XSS) vulnerability in the `/system/api/saveNode` endpoint. An authenticated user with a permission to edit pages can bypass the HTML sanitizer by injecting an event handler attribute without whitespace before the attribute name.

For example, the sanitizer misses:

```html
<a href="#"onclick="alert('kn1ph')">click me</a>
```

The important bypass is:

```html
href="#"onclick=
```

The payload is stored in the generated page files and executes when a user clicks the injected link.

## Details

The issue is caused by regex-based HTML sanitization that expects whitespace before event handler attributes. Because the sanitizer expects a pattern like:

```html
href="#" onclick="..."
```

It fails to remove an event handler when it is written without whitespace:

```html
href="#"onclick="..."
```

Browsers still parse `onclick` as a valid event handler attribute, so the JavaScript executes when the element is clicked.

Affected endpoint:

```text
POST /system/api/saveNode?site_token=[VALID_SITE_TOKEN]
```

Affected parameter:

```text
node.body
```

## PoC

1. Log in to HaxCMS and edit any existing page.

2. Capture the page save request in Burp Suite:

```text
POST /system/api/saveNode?site_token=[VALID_SITE_TOKEN]
```
3. In the JSON request body, modify only the `node.body` value.

Change:
```json
"body":"...existing page content...\n"
```
To:
```json
"body":"...existing page content...\n<a href=\"#\"onclick=\"alert('kn1ph')\">click me</a>\n"
```

5. Forward the request.

6. Open the edited page and click `click me`.

Result:

The JavaScript will execute and the alert will pop up. 

It was confirmed that the payload is stored in the generated page files, including `index.html`.

## Impact

An authenticated user with permissions to edit the page can inject stored JavaScript into the page content. If a privileged user interacts with the injected element while authenticated, the attacker controlled JavaScript will execute in that user’s browser.

Based on local testing, the XSS can access browser-exposed HaxCMS data such as `localStorage.jwt` and `window.appSettings`, including API paths and tokens available to the authenticated user.

This may allow an attacker to perform actions as the victim within the limits of the exposed tokens and the victim’s permissions and possibly chain more vulnerabilities.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-g2g8-95qg-v35h
- https://nvd.nist.gov/vuln/detail/CVE-2026-48527
- https://github.com/haxtheweb/issues
