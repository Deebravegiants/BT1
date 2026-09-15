# [C] WeGIA Vulnerable to Remote Code Execution (RCE) via OS Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-28409
Aliases: GHSA-5m5g-q2vv-rv3r
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28409
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.6.5, a critical Remote Code Execution (RCE) vulnerability exists in the WeGIA application's database restoration functionality. An attacker with administrative access (which can be obtained via the previously reported Authentication Bypass) can execute arbitrary OS commands on the server by uploading a backup file with a specifically crafted filename. Version 3.6.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28409.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-5m5g-q2vv-rv3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-28409
