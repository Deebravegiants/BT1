# [H] Greenshot Vulnerable to OS Command Injection via ExternalCommand Plugin

## Summary
Severity: High
Advisory: CVE-2026-22035
Aliases: GHSA-7hvw-q8q5-gpmj
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-22035
Type: osv

## Details
Greenshot is an open source Windows screenshot utility. Versions 1.3.310 and below arvulnerable to OS Command Injection through unsanitized filename processing. The FormatArguments method in ExternalCommandDestination.cs:269 uses string.Format() to insert user-controlled filenames directly into shell commands without sanitization, allowing attackers to execute arbitrary commands by crafting malicious filenames containing shell metacharacters. This issue is fixed in version 1.3.311.

## References
- https://github.com/greenshot/greenshot/releases/tag/v1.3.311
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22035.json
- https://github.com/greenshot/greenshot/security/advisories/GHSA-7hvw-q8q5-gpmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22035
- https://github.com/greenshot/greenshot/commit/5dedd5c9f0a9896fa0af1d4980d875a48bf432cb
