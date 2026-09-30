# [H] BIT-suitecrm-2021-42840

## Summary
Severity: High
Advisory: BIT-suitecrm-2021-42840
Aliases: CVE-2021-42840
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2021-42840
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=0 <7.11.19

## Details
SuiteCRM before 7.11.19 allows remote code execution via the system settings Log File Name setting. In certain circumstances involving admin account takeover, logger_file_name can refer to an attacker-controlled PHP file under the web root, because only the all-lowercase PHP file extensions were blocked. NOTE: this issue exists because of an incomplete fix for CVE-2020-28328.

## References
- http://packetstormsecurity.com/files/165001/SuiteCRM-7.11.18-Remote-Code-Execution.html
- https://docs.suitecrm.com/admin/releases/7.11.x/#_7_11_19
- https://github.com/rapid7/metasploit-framework/commits/master/modules/exploits/linux/http/suitecrm_log_file_rce.rb
- https://suitecrm.com/time-to-upgrade-suitecrm-7-11-19-7-10-30-lts-released/
- https://theyhack.me/SuiteCRM-RCE-2/
- https://nvd.nist.gov/vuln/detail/CVE-2021-42840
