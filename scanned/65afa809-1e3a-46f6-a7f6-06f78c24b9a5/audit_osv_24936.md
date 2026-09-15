# [H] OS Command Injection via GIT_PATH in pymedusa

## Summary
Severity: High
Advisory: CVE-2023-28627
Aliases: GHSA-6589-x6f5-cgg9
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-28627
Type: osv

## Details
pymedusa is an automatic video library manager for TV Shows. In versions prior 1.0.12 an attacker with access to the web interface can update the git executable path in /config/general/ > advanced settings with arbitrary OS commands. An attacker may exploit this vulnerability to take execute arbitrary OS commands as the user running the pymedusa program. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28627.json
- https://github.com/pymedusa/Medusa/security/advisories/GHSA-6589-x6f5-cgg9
- https://nvd.nist.gov/vuln/detail/CVE-2023-28627
- https://github.com/pymedusa/Medusa/commit/66d4be8f0872bd5ddcdc5c5a58cb014d22834a45
