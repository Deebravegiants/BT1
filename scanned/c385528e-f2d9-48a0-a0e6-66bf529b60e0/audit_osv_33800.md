# [C] WeGIA OS Command Injection in debug_info.php parameter 'branch'

## Summary
Severity: Critical
Advisory: CVE-2025-50201
Aliases: GHSA-52p5-5fmw-9hrf
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-50201
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.4.2, an OS Command Injection vulnerability was identified in the /html/configuracao/debug_info.php endpoint. The branch parameter is not properly sanitized before being concatenated and executed in a shell command on the server's operating system. This flaw allows an unauthenticated attacker to execute arbitrary commands on the server with the privileges of the web server user (www-data). This issue has been patched in version 3.4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50201.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-52p5-5fmw-9hrf
- https://nvd.nist.gov/vuln/detail/CVE-2025-50201
- https://github.com/LabRedesCefetRJ/WeGIA/commit/45f32ad1d52775fc99f3c90075c8136c6d4d1d3d
