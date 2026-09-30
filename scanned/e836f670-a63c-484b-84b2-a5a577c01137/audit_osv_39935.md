# [C] Nagios Core / XI Authenticated RCE via Unfiltered NOTIFICATION-Family Macro Substitution

## Summary
Severity: Critical
Advisory: CVE-2026-48554
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-48554
Type: osv

## Details
Nagios Core before 4.5.14 and Nagios XI before 2026R1.7 are vulnerable to authenticated remote code execution via unfiltered NOTIFICATION-family macro substitution through the com_data parameter. When a notification command references $NOTIFICATIONCOMMENT$ or $NOTIFICATIONAUTHOR$ in a shell-reachable position, authenticated UI users can run arbitrary commands as the nagios user. Exploitation requires a non-default configuration in which a notification command references these macros in a shell-executed command line.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48554.json
- https://github.com/NagiosEnterprises/nagioscore/blob/master/Changelog
- https://nvd.nist.gov/vuln/detail/CVE-2026-48554
- https://www.vulncheck.com/advisories/nagios-core-xi-authenticated-rce-via-unfiltered-notification-family-macro-substitution
- https://www.nagios.com/security-disclosures/nagios-core/
