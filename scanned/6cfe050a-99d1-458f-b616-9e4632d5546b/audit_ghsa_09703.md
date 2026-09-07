# [H] SiYuan Desktop: Stored XSS in imported .sy.zip content leads to arbitrary command execution

## Summary
Severity: High
Advisory: GHSA-ff66-236v-p4fg
CVE: CVE-2026-34585
CWE: CWE-79, CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-ff66-236v-p4fg
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260329142331-918d1bd9f967

## Details
### Summary
A vulnerability allows crafted block attribute values to bypass server-side attribute escaping when an HTML entity is mixed with raw special characters. An attacker can embed a malicious IAL value inside a `.sy` document, package it as a `.sy.zip`, and have the victim import it through the normal `Import -> SiYuan .sy.zip` workflow. Once the note is opened, the malicious attribute breaks out of its original HTML context and injects an event handler, resulting in stored XSS. In the Electron desktop client, this XSS reaches remote code execution because injected JavaScript runs with access to Node/Electron APIs.

### Details
The issue is caused by a logic regression in `escapeNodeAttributeValues` in `kernel/filesys/tree.go`.
Previously, the escaping logic converted `node.KramdownIAL` with `parse.IAL2Map(...)` before deciding whether a value needed escaping. That conversion unescaped existing entities first, so mixed values such as:
```
&amp;" onmouseenter="alert('IAL-XSS')
```
were still recognized as unsafe and escaped correctly.
The logic changed to inspect raw `KramdownIAL` values directly. The new `needsEscapeForValue` implementation returns `false` as soon as it sees any known entity such as `&amp;`, `&quot;`, `&lt;`, or `&gt;`. This means a value containing both an entity and an unescaped raw quote bypasses escaping entirely.

That bypass becomes exploitable because the renderer later inserts block IAL values directly into HTML attributes. A payload like:
```
&amp;" onmouseenter="require('child_process').exec('calc')
```
can be rendered into HTML equivalent to:
```
<div title="&amp;" onmouseenter="require('child_process').exec('calc')">
```
This creates a stored XSS condition. In SiYuan Desktop, the Electron renderer runs with Node.js integration available, so attacker-controlled JavaScript can invoke Node APIs directly. As a result, the issue is not limited to script execution in the page context and becomes arbitrary command execution on the victim’s machine.

The stored XSS path was validated by importing a crafted `.sy.zip` through the normal GUI and triggering JavaScript execution from the rendered block. Because the same injected JavaScript runs in the privileged Electron renderer, this is an RCE issue in the desktop client.

### PoC
1. Start SiYuan Desktop `v3.6.1`.
2. Prepare a crafted `.sy.zip` containing a .sy document with a block IAL property such as:
```
"title": "&amp;\" onmouseenter=\"require('child_process').exec('calc')"
```
3. In the UI, right-click any notebook.
4. Select `Import -> SiYuan .sy.zip`.
5. Import the crafted archive.
6. Open the imported note.
7. Move the mouse over the affected paragraph block.
8. Observe that the injected JavaScript executes.
9. On Windows, `calc.exe` launches, demonstrating arbitrary command execution.

### Impact
This vulnerability allows an attacker to deliver a malicious `.sy.zip` file that executes attacker-controlled JavaScript after import. In the desktop application, that JavaScript runs with Node/Electron privileges and can execute arbitrary operating system commands under the victim’s account. This makes the bug equivalent to local code execution triggered by importing and opening attacker-supplied content.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-ff66-236v-p4fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34585
- https://github.com/siyuan-note/siyuan/issues/17246
- https://github.com/siyuan-note/siyuan/commit/918d1bd9f967d888f474f6764744a3d8cca4a501
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.2
