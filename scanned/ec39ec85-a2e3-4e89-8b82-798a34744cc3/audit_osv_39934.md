# [C] Nagios Core / XI Authenticated RCE via Custom-Variable Macro Injection

## Summary
Severity: Critical
Advisory: CVE-2026-48553
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-48553
Type: osv

## Details
Nagios Core before 4.5.13 and Nagios XI before 2026R1.5 are vulnerable to authenticated remote code execution via custom-variable macro injection through the Nagios Remote Data Processor (NRDP). When a custom variable defined on a host, service, or contact is referenced in a shell-executed command line, an authenticated attacker with NRDP access can inject OS commands through the macro value. Exploitation requires a non-default configuration in which a custom variable is defined and referenced in a shell-executed command.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48553.json
- https://github.com/NagiosEnterprises/nagioscore/blob/master/Changelog
- https://nvd.nist.gov/vuln/detail/CVE-2026-48553
- https://www.vulncheck.com/advisories/nagios-core-xi-authenticated-rce-via-custom-variable-macro-injection
- https://www.nagios.com/security-disclosures/nagios-core/
