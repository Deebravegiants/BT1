# [C] Renovate before 44.14.7 Command Injection via distributionType

## Summary
Severity: Critical
Advisory: CVE-2026-88889
Aliases: GHSA-f2v7-35mm-3hx7
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88889
Type: osv

## Details
Renovate before 44.14.7 contains a command injection vulnerability in the Maven Wrapper manager that allows attackers to execute arbitrary commands by specifying a malicious distributionType parameter in maven-wrapper.properties. Attackers can inject shell commands through unescaped distributionType values to achieve remote code execution when Renovate processes Maven Wrapper updates in binarySource=docker mode.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88889.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-f2v7-35mm-3hx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-88889
- https://www.vulncheck.com/advisories/renovate-before-44.14.7-command-injection-via-distributiontype
