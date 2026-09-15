# [H] CVE-2026-73570

## Summary
Severity: High
Advisory: CVE-2026-73570
CVSS: 8.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73570
Type: osv

## Details
A remote code execution vulnerability exists in Zimbra Collaboration (ZCS) before 10.1.20 when the optional zimbra-snmp package is installed and SNMP notifications are enabled. Due to improper sanitization of untrusted input during SNMP notification processing, an unauthenticated attacker can send specially crafted SMTP requests that may result in execution of arbitrary operating system commands as the Zimbra user.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-73570
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73570.json
- https://moje.cert.pl/komunikaty/2026/145/aktywnie-wykorzystywana-podatnosc-w-zimbra-collaboration-suite/
- https://nvd.nist.gov/vuln/detail/CVE-2026-73570
