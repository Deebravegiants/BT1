# [C] CVE-2018-16763

## Summary
Severity: Critical
Advisory: CVE-2018-16763
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-09
Source: https://osv.dev/vulnerability/CVE-2018-16763
Type: osv

## Details
FUEL CMS 1.4.1 allows PHP Code Evaluation via the pages/select/ filter parameter or the preview/ data parameter. This can lead to Pre-Auth Remote Code Execution.

## References
- https://github.com/daylightstudio/FUEL-CMS/issues/478
- http://packetstormsecurity.com/files/153696/fuelCMS-1.4.1-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/160080/Fuel-CMS-1.4-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/164756/Fuel-CMS-1.4.1-Remote-Code-Execution.html
- https://0xd0ff9.wordpress.com/2019/07/19/from-code-evaluation-to-pre-auth-remote-code-execution-cve-2018-16763-bypass/
- https://www.exploit-db.com/exploits/47138
