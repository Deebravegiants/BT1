# [H] Open WebUI: Stored XSS in Mermaid Markdown Preview

## Summary
Severity: High
Advisory: GHSA-v8qj-hxv7-mgvv
CVE: CVE-2026-54011
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-v8qj-hxv7-mgvv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

Open WebUI renders Mermaid blocks from Markdown files in the file preview panel and inserts the generated SVG into the DOM using `innerHTML`.

Because Mermaid is configured with `securityLevel: 'loose'`, attacker-controlled Mermaid content can be rendered unsafely in this flow. A working payload was validated through the Markdown preview path, resulting in JavaScript execution in the victim’s browser under the application origin.

This is a confirmed stored XSS vulnerability reachable through normal product functionality.

## Affected Version

- `main`
- Reproduced on `v0.8.12`

## Affected Code

Mermaid is initialized in permissive mode:

https://github.com/open-webui/open-webui/blob/9bd84258d09eefe7bf975878fb0e31a5dadfe0f8/src/lib/utils/index.ts#L1698
The file preview path renders Mermaid output and injects the returned SVG into the DOM:

https://github.com/open-webui/open-webui/blob/9bd84258d09eefe7bf975878fb0e31a5dadfe0f8/src/lib/components/chat/FileNav/FilePreview.svelte#L133

## Impact

A successful exploit allows JavaScript execution in the victim’s browser under the Open WebUI origin when a malicious Markdown file is opened in the preview panel.

## PoC

A malicious `.md` file containing the follwowing contents can be used to trigger the bug:
````
```mermaid
flowchart LR
  A[click me]
  click A href "javascript:alert(document.domain)" "x"
```
````
Steps to reproduce: 
1- Create a new chat 
2- Enable Code Interpreter and browse and upload the file with `.md` extension. 
<img width="331" height="258" alt="image" src="https://github.com/user-attachments/assets/bce2b754-56d1-4da1-90a9-22bcb93269f2" />
3- Clicking on the file, and clicking `click me` should pop an alert
<img width="1103" height="485" alt="image" src="https://github.com/user-attachments/assets/18754486-799b-434e-a2fc-dd7c09956a29" />
 

## Remediation

Since `mermaid` has `DOMPurify` as a built-in, it is recommended to use the `strict` mode instead of `loose`.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-v8qj-hxv7-mgvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-54011
- https://github.com/advisories/GHSA-v8qj-hxv7-mgvv
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2759.yaml
- https://pypi.org/project/open-webui
