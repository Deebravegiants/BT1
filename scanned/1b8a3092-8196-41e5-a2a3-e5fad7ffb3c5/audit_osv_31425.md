# [H] Arbitrary Code Execution in Kong Insomnia Desktop Application

## Summary
Severity: High
Advisory: CVE-2025-1087
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:L/SC:H/SI:H/SA:L)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-1087
Type: osv

## Details
Kong Insomnia Desktop Application before 11.0.2 contains a template injection vulnerability that allows attackers to execute arbitrary code. The vulnerability exists due to insufficient validation of user-supplied input when processing template strings, which can lead to arbitrary JavaScript execution in the context of the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1087.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1087
- https://github.com/Kong/insomnia
- https://tantosec.com/blog/2025/06/insomnia-api-client-template-injection/
