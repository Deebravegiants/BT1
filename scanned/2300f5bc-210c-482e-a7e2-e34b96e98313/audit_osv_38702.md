# [C] Remote code execution via JavaScript injection in `BrowserAutomation::PlaywrightService`

## Summary
Severity: Critical
Advisory: CVE-2026-41512
Aliases: GHSA-r27j-xxgx-f5vr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-41512
Type: osv

## Details
ai-scanner is an AI model safety scanner built on NVIDIA garak. From version 1.0.0 to before version 1.4.1, there is a remote code execution vulnerability via JavaScript injection in `BrowserAutomation::PlaywrightService`. This issue has been patched in version 1.4.1.

## References
- https://github.com/0din-ai/ai-scanner/releases/tag/v1.4.1
- https://github.com/0din-ai/ai-scanner/security/advisories/GHSA-r27j-xxgx-f5vr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41512.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41512
