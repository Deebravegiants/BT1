# [C] Renovate before 44.14.7 Command Injection via depName

## Summary
Severity: Critical
Advisory: CVE-2026-88885
Aliases: GHSA-mpf8-qxrw-gq3w
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88885
Type: osv

## Details
Renovate before 44.14.7 contains a command injection vulnerability in the gomod manager when processing unescaped depName parameters in import-path update commands with binarySource=docker mode. Attackers can inject shell metacharacters through malicious dependency names to execute arbitrary commands as the Renovate user during Go module major version updates with postUpdateOptions gomodUpdateImportPaths enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88885.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-mpf8-qxrw-gq3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-88885
- https://www.vulncheck.com/advisories/renovate-before-44.14.7-command-injection-via-depname
