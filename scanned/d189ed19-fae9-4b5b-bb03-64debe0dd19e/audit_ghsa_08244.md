# [H] Kirby CMS vulnerable to cross-site scripting (XSS) from links in KirbyTags and image blocks in the site frontend

## Summary
Severity: High
Advisory: GHSA-qvjf-922g-pj44
CVE: CVE-2026-45368
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-qvjf-922g-pj44
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.1
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.4.1

## Details
### TL;DR

This vulnerability affects all Kirby sites that allow the use of the `(link: …)` KirbyTag, the `link:` parameter of the `(image: …)` KirbyTag, the built-in `image` block with a link or the HTML importer for blocks, when content is authored by users who may not be fully trusted. The attack requires an authenticated Panel user with update permission to any `textarea` or `blocks` field, or write access to content files through another vector (e.g. a frontend form or content sync pipeline). Another attack vector is the use of `Html::a()` or `Html::link()` with untrusted user input.

**This vulnerability is of high severity for affected sites.**

Kirby sites are *not* affected if none of the mentioned KirbyTags or block types are used, or if every user who can edit content is fully trusted. The attack only surfaces in the site frontend (i.e. in its templates). The Panel itself is unaffected and will not execute JavaScript that was injected into the `textarea` or `blocks` field content.

---

### Introduction

Cross-site scripting (XSS) is a type of vulnerability that allows to execute any kind of JavaScript code inside the site frontend or Panel session of the same or other users. In the Panel, a harmful script can for example trigger requests to Kirby's API with the permissions of the victim.

In a *stored* XSS attack, the malicious payload is saved into the content data and has the potential to affect other users or site visitors.

Such vulnerabilities are critical if a consuming application might have potential attackers in its group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on the site, other JavaScript-powered attacks are possible.

A specific class of stored XSS exploits the `javascript:` URI scheme in HTML `<a href>` attributes. When a browser processes a click action on a link with `href="javascript:…"`, it executes the value as JavaScript in the origin of the current page. Because the site usually runs on the same origin as the Panel API, a successful exploit in the site frontend can give the attacker full control of the victim's Panel session.

### Affected components

Kirby provides four first-party renderers that produce `<a href="…">` output from editor-supplied field values:

1. The `(link: …)` KirbyTag
2. The `link:` parameter of the `(image: …)` KirbyTag, when the parameter does not resolve to a known file or `'self'`
3. The link field of the built-in `image` block
4. The HTML importer for the blocks field (which accepted the same malicious input as the `image` block link field)

### Impact

In affected releases, the underlying URL methods for these components did not filter out malicious URL values that resolve to script execution. While simple `javascript:` URLs were already deactivated by treating them as a relative path and prepending a single slash to the URL, the use of URLs of the format `javascript://x%0A…` bypasses this protection. The `vbscript:`, `data:`, `livescript:`, `mocha:` and `jar:` schemes are affected by the same underlying gap.

The vulnerability allows attackers to inject malicious links into content. The malicious links would then be rendered on the site frontend. If a site visitor or logged in user browsing the site would click such a link, the malicious script code would then be executed in the browser.

### Patches

The problem has been patched in [Kirby 4.9.1](https://github.com/getkirby/kirby/releases/tag/4.9.1) and [Kirby 5.4.1](https://github.com/getkirby/kirby/releases/tag/5.4.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, a new `Url::hasDangerousScheme()` method detects URI schemes that must never appear in a rendered `href` or `src` attribute (`javascript:`, `vbscript:`, `livescript:`, `mocha:`, `jar:`, `data:`).

`Url::isAbsolute()` now returns `false` for any URL that `hasDangerousScheme()` identifies as dangerous, so the URL component no longer passes these values through `makeAbsolute()` unchanged.

`Html::link()` now replaces the `href` with an empty string when a dangerous scheme is detected, so the rendered `<a>` tag links back to the current page rather than executing the injected script.

The HTML importer for blocks strips link targets with a dangerous scheme.

Due to the hardening in these underlying URL methods, the affected KirbyTags and block no longer allow dangerous schemes in link targets.

### Credits

Kirby thanks @offset for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-qvjf-922g-pj44
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.1
- https://github.com/getkirby/kirby/releases/tag/5.4.1
