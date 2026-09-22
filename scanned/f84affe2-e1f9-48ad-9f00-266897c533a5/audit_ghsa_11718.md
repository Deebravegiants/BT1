# [H] OpenClaw: Arbitrary code execution via unvalidated WebView JavascriptInterface

## Summary
Severity: High
Advisory: GHSA-cxmw-p77q-wchg
CVE: CVE-2026-35643
CWE: CWE-77, CWE-940
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-cxmw-p77q-wchg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Android Canvas WebView pages from untrusted origins could invoke the JavascriptInterface bridge and inject instructions into the app.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `8b02ef133275be96d8aac2283100016c8a7f32e5`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- apps/android/app/src/main/java/ai/openclaw/app/ui/CanvasScreen.kt now snapshots page origin and rejects untrusted bridge calls.
- apps/android/app/src/main/java/ai/openclaw/app/node/CanvasActionTrust.kt centralizes trusted origin and path validation for the bridge.

OpenClaw thanks @cyjhhh for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cxmw-p77q-wchg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35643
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/8b02ef133275be96d8aac2283100016c8a7f32e5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-code-execution-via-unvalidated-webview-javascriptinterface
