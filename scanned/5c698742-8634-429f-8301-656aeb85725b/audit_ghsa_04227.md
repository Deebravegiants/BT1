# [H] Docling: Unsafe Playwright-based HTML Rendering

## Summary
Severity: High
Advisory: GHSA-pj2v-ggqh-cmq2
CVE: CVE-2026-44016
CWE: CWE-918, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-pj2v-ggqh-cmq2
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=2.82.0 <2.91.0

## Details
### Impact
In versions `>= 2.82.0, < 2.91.0`, if the HTML backend was explicitly configured for rendering (rendering option by default deactivated), then the Playwright-based rendering feature could allow JavaScript execution and unrestricted network access when processing untrusted HTML documents. An attacker could craft malicious HTML that executes arbitrary JavaScript in the rendering context or makes unauthorized network requests to internal services, potentially leading to SSRF attacks, data exfiltration, or remote code execution in the rendering environment.

### Patches
Fixed in version 2.91.0. The rendering context now explicitly disables JavaScript execution (`java_script_enabled=False`) and implements network isolation controls. When `enable_remote_fetch` is disabled, the browser operates in offline mode, preventing all network requests.

### Workarounds
Refrain from using `render_page=True` when processing untrusted HTML documents.

### References
- Fix release: [v2.91.0](https://github.com/docling-project/docling/releases/tag/v2.91.0)

## References
- https://github.com/docling-project/docling/security/advisories/GHSA-pj2v-ggqh-cmq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44016
- https://access.redhat.com/security/cve/CVE-2026-44016
- https://bugzilla.redhat.com/show_bug.cgi?id=2492339
- https://github.com/docling-project/docling
- https://github.com/docling-project/docling/releases/tag/v2.91.0
- https://github.com/pypa/advisory-database/tree/main/vulns/docling/PYSEC-2026-2142.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44016.json
