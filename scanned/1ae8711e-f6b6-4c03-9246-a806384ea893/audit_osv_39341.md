# [C] GitButler: Link injection via forge integration enables arbitrary script execution

## Summary
Severity: Critical
Advisory: CVE-2026-45261
Aliases: GHSA-xpmj-536r-9fc6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45261
Type: osv

## Details
GitButler is a modern Git-based version control interface for AI-powered workflows. Prior to 0.19.7, a emote code execution vulnerability exists in the Tauri-based GitButler desktop application. An attacker can inject a malicious link in a pull request body, which if clicked by the user allows for arbitrary script execution in the Tauri webview. Users that have not enabled forge integration are not at risk. This vulnerability is fixed in 0.19.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45261.json
- https://github.com/gitbutlerapp/gitbutler/security/advisories/GHSA-xpmj-536r-9fc6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45261
