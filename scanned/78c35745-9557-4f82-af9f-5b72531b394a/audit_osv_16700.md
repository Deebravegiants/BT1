# [H] CVE-2019-9082

## Summary
Severity: High
Advisory: CVE-2019-9082
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9082
Type: osv

## Details
ThinkPHP before 3.2.4, as used in Open Source BMS v1.1.1 and other products, allows Remote Command Execution via public//?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]= followed by the command.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-9082
- https://github.com/xiayulei/open_source_bms/issues/33
- http://packetstormsecurity.com/files/157218/ThinkPHP-5.0.23-Remote-Code-Execution.html
- https://www.exploit-db.com/exploits/46488/
