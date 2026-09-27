# [C] Windscribe for Linux 'changeMTU' local privilege escalation

## Summary
Severity: Critical
Advisory: CVE-2025-65199
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-10
Source: https://osv.dev/vulnerability/CVE-2025-65199
Type: osv

## Details
A command injection vulnerability exists in Windscribe for Linux Desktop App that allows a local user who is a member of the windscribe group to execute arbitrary commands as root via the 'adapterName' parameter of the 'changeMTU' function. Fixed in Windscribe v2.18.3-alpha and v2.18.8.

## References
- https://www.cve.org/CVERecord?id=CVE-2025-65199
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65199.json
- https://hackingbydoing.wixsite.com/hackingbydoing/post/windscribe-vpn-local-privilege-escalation
- https://nvd.nist.gov/vuln/detail/CVE-2025-65199
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-25-343-01.json
- https://github.com/Windscribe/Desktop-App/compare/v2.18.2...v2.18.3?diff=unified&w#diff-57e27ab201a1a612609087b839e03bf87a5a063ffcc3f465a6245469bc102754
- https://github.com/Windscribe/Desktop-App/compare/v2.18.2...v2.18.3?diff=unified&w#diff-cfc5df17057ed92112ae70a42c81c57c79f434429210ff881fb0771cf8e39b4c
- https://github.com/Windscribe/Desktop-App
