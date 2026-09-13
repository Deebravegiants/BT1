# [H] SiYuan: Stored XSS in Bazaar marketplace via package README event handlers

## Summary
Severity: High
Advisory: GHSA-w7cg-whh7-xp28
CVE: CVE-2026-54070
CWE: CWE-184, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-w7cg-whh7-xp28
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
## Summary

`renderPackageREADME` in `kernel/bazaar/readme.go` renders a Bazaar package README from Markdown to HTML with the lute engine and `SetSanitize(true)`. The lute sanitizer is an event-handler blocklist: `allowAttr` rejects only attribute names present in a fixed `eventAttrs` map copied from the w3schools legacy handler list.

That map omits modern event handlers. `onpointerover`, `onpointerdown`, `onauxclick`, `onbeforetoggle`, `onfocusin`, `onanimationstart`, and `ontransitionend` are not in the list, so the sanitizer passes them through verbatim on any tag.

The frontend assigns the rendered HTML to `mdElement.innerHTML` in `app/src/config/bazaar.ts` with no client-side DOMPurify on this path, into a normal element in the main document (no iframe, no sandbox). The kernel sends no Content-Security-Policy, X-Frame-Options, or X-Content-Type-Options header on any response, so an inline handler runs when its event fires.

The README is rendered when an Administrator opens a package in Settings → Marketplace, after the one-time marketplace trust consent. Install is not required.

Result: a third-party Bazaar package author runs JavaScript in the Administrator's authenticated SiYuan origin when the Administrator views and interacts with the package listing, and gains full control of the workspace.

## Affected

siyuan-note/siyuan, `<= 3.6.5` (latest release, 2026-04-21). Confirmed live-exploitable on the `b3log/siyuan:v3.6.5` image; identical code on `master` HEAD.
Condition: the Administrator has accepted the marketplace trust consent (`bazaar.trust`, default false) and browses community Bazaar packages. The lute dependency pin is `github.com/88250/lute v1.7.7-0.20260419134724-bb68012f231d`.
Both the online browse path (`getBazaarPackageREADME`) and the installed-package path (`getInstalledPlugin`) reach the same sink.

## Root cause

`render/sanitizer.go:225-232` (lute): `allowAttr(name)` returns false only when `name` exists in the `eventAttrs` map, an attribute denylist rather than an allowlist.
`render/sanitizer.go:235-334` (lute): `eventAttrs` is the w3schools handler list and contains no pointer, beforetoggle, focusin, animation, or transition handlers.
`kernel/bazaar/readme.go:108-118`: `renderPackageREADME` builds the engine with `SetSanitize(true)` and returns the HTML string to the caller.
`kernel/bazaar/readme.go:48-88`: `GetBazaarPackageREADME` renders an untrusted remote package README; `kernel/api/bazaar.go` exposes it at `/api/bazaar/getBazaarPackageREADME` (`router.go:423`, `CheckAuth`).
`app/src/config/bazaar.ts:600` and `:609`: `mdElement.innerHTML = data.preferredReadme` / `= response.data.html`, no DOMPurify, target is a plain div.
Kernel HTTP responses carry no CSP/X-Frame-Options/X-Content-Type-Options header (live-confirmed), so an inline handler is not blocked.

## Reproduction

`b3log/siyuan:v3.6.5` Docker, default config, access auth code set, marketplace trust accepted.

1. Place a package whose README carries a non-blocklisted handler (an online community package produces the identical render at browse time):

```
mkdir -p workspace/data/plugins/evil-plugin
cat > workspace/data/plugins/evil-plugin/plugin.json <<'JSON'
{"name":"evil-plugin","author":"x","version":"1.0.0","minAppVersion":"3.0.0",
 "displayName":{"default":"Evil"},"description":{"default":"poc"},
 "readme":{"default":"README.md"},"backends":["all"],"frontends":["all"]}
JSON
printf '<div onpointerover="alert(document.domain)">plugin description</div>\n' \
  > workspace/data/plugins/evil-plugin/README.md
```

2. Request the rendered README the way the Marketplace panel does:

```
curl -s -X POST http://127.0.0.1:6806/api/bazaar/getInstalledPlugin \
  -H "Authorization: Token <API-TOKEN>" -H "Content-Type: application/json" \
  -d '{"frontend":"all","keyword":""}'
```

Response `data.packages[].preferredReadme` contains the handler verbatim:

```
<div onpointerover="alert(document.domain)">plugin description</div>
```

A control `<img src=x onerror=...>` in the same README is returned HTML-escaped and inert.

3. In Settings → Marketplace, open the package and move the pointer over its README.

Live-verified: the rendered HTML is assigned to `mdElement.innerHTML` (no CSP, no sandbox) and the `onpointerover` handler executes `alert(document.domain)` in the SiYuan origin on hover. Handlers do not auto-fire on insertion; one pointer/focus/click interaction on the listing triggers them.

## Impact

- JavaScript execution in the Administrator's authenticated origin on a marketplace package view plus one hover/click/focus, no install needed.
- Theft of the kernel API token (`conf.api.token`), which grants full Administrator API access.
- Pivot to `installBazaarPlugin` and kernel control; the runtime image ships a shell.
- A single malicious community package reaches every instance that views its listing.

## Credit

Jan Kahmen, [turingpoint](https://turingpoint.de) (jan@turingpoint.de)

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-w7cg-whh7-xp28
- https://nvd.nist.gov/vuln/detail/CVE-2026-54070
- https://github.com/siyuan-note/siyuan
