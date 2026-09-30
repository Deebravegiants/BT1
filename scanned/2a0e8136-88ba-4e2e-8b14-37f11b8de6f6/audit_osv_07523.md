# [H] BIT-suitecrm-2020-28328

## Summary
Severity: High
Advisory: BIT-suitecrm-2020-28328
Aliases: CVE-2020-28328
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2020-28328
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=0 <7.11.17

## Details
SuiteCRM before 7.11.17 is vulnerable to remote code execution via the system settings Log File Name setting. In certain circumstances involving admin account takeover, logger_file_name can refer to an attacker-controlled .php file under the web root.

## References
- http://packetstormsecurity.com/files/159937/SuiteCRM-7.11.15-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/162975/SuiteCRM-Log-File-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/165001/SuiteCRM-7.11.18-Remote-Code-Execution.html
- https://github.com/mcorybillington/SuiteCRM-RCE
- https://suitecrm.com/suitecrm-7-11-17-7-10-28-lts-versions-released/
- https://nvd.nist.gov/vuln/detail/CVE-2020-28328
