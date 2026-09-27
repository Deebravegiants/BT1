# [H] HomeAssistant-Tapo-Control Code Injection Vulnerability in issues.yml Workflow

## Summary
Severity: High
Advisory: CVE-2025-55192
Aliases: GHSA-xccg-43hx-c846
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-14
Source: https://osv.dev/vulnerability/CVE-2025-55192
Type: osv

## Details
HomeAssistant-Tapo-Control offers Control for Tapo cameras as a Home Assistant component. Prior to commit 2a3b80f, there is a code injection vulnerability in the GitHub Actions workflow .github/workflows/issues.yml. It does not affect users of the Home Assistant integration itself — it only impacts the GitHub Actions environment for this repository. The vulnerable workflow directly inserted user-controlled content from the issue body (github.event.issue.body) into a Bash conditional without proper sanitization. A malicious GitHub user could craft an issue body that executes arbitrary commands on the GitHub Actions runner in a privileged context whenever an issue is opened. The potential impact is limited to the repository’s CI/CD environment, which could allow access to repository contents or GitHub Actions secrets. This issue has been patched via commit 2a3b80f. Workarounds involve disabling the affected workflow (issues.yml), replacing the unsafe Bash comparison with a safe quoted grep (or a pure GitHub Actions expression check), or ensuring minimal permissions in workflows (permissions: block) to reduce possible impact.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55192.json
- https://github.com/JurajNyiri/HomeAssistant-Tapo-Control/security/advisories/GHSA-xccg-43hx-c846
- https://nvd.nist.gov/vuln/detail/CVE-2025-55192
- https://securitylab.github.com/advisories/GHSL-2025-101_homeassistant-tapo-control
- https://github.com/JurajNyiri/HomeAssistant-Tapo-Control/commit/2a3b80ff128ddf4f410c97dd47a94343792ce43c
