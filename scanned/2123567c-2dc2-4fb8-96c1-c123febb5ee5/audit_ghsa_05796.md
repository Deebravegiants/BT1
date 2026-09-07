# [H] ngx-extended-pdf-viewer bundles a version of pdf.js vulnerable to CVE-2026-16633

## Summary
Severity: High
Advisory: GHSA-w9hm-4m3m-fxmm
CWE: CWE-1103
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-w9hm-4m3m-fxmm
Type: github-advisory

## Affected
- npm: `ngx-extended-pdf-viewer` — affected >=27.0.0-rc.0 <29.0.0-rc.3

## Details
ngx-extended-pdf-viewer embeds a fork of Mozilla's pdf.js rather than depending on pdfjs-dist, so this vulnerability is not visible to dependency scanners through package.json.

### Impact
Opening a malicious PDF can execute attacker-controlled JavaScript in the context of the hosting page. Upstream advisory: GHSA-hq66-cqwq-w95j / CVE-2026-16633.

### Exposure. 
The sandbox half of the issue requires enableScripting, which pdf.js enables by default but this library does not — so the default configuration was less exposed than upstream's. The other half concerns XFA rich text and is reachable whenever enableXfa is true, which is the default here. Do not assume the default configuration was safe.

### Patches
29.0.0-rc.3 cherry-picks Mozilla's fix (pdf.js 6.2.108) into both the stable and bleeding-edge engines. Only the latest release receives security updates.

### Workarounds
Set pdfDefaultOptions.enableXfa = false if you do not need XFA forms, and/or apply a CSP disallowing inline script-src.

### Verifying. 
From 29.0.0 the package ships sbom.json and vex.json. The SBOM records the applied fix as a CycloneDX pedigree.patches entry; the VEX carries a resolved_with_pedigree statement so scanners stop flagging the engine's nominal version.

## References
- https://github.com/stephanrauh/ngx-extended-pdf-viewer/security/advisories/GHSA-w9hm-4m3m-fxmm
- https://github.com/stephanrauh/ngx-extended-pdf-viewer
