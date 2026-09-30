# [C] CVE-2018-25270

## Summary
Severity: Critical
Advisory: CVE-2018-25270
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2018-25270
Type: osv

## Details
ThinkPHP 5.0.23 contains a remote code execution vulnerability that allows unauthenticated attackers to execute arbitrary PHP code by invoking functions through the routing parameter. Attackers can craft requests to the index.php endpoint with malicious function parameters to execute system commands with application privileges.

## References
- https://github.com/top-think/framework/
- https://thinkphp.cn
- https://www.vulncheck.com/advisories/thinkphp-remote-code-execution-via-invokefunction
- https://www.exploit-db.com/exploits/45978
