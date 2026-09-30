# [C] CVE-2014-8322

## Summary
Severity: Critical
Advisory: CVE-2014-8322
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-31
Source: https://osv.dev/vulnerability/CVE-2014-8322
Type: osv

## Details
Stack-based buffer overflow in the tcp_test function in aireplay-ng.c in Aircrack-ng before 1.2 RC 1 allows remote attackers to execute arbitrary code via a crafted length parameter value.

## References
- http://aircrack-ng.blogspot.com/2014/10/aircrack-ng-12-release-candidate-1.html
- http://packetstormsecurity.com/files/128943/Aircrack-ng-1.2-Beta-3-DoS-Code-Execution.html
- http://www.exploit-db.com/exploits/35018
- https://exchange.xforce.ibmcloud.com/vulnerabilities/98459
- https://github.com/aircrack-ng/aircrack-ng/commit/091b153f294b9b695b0b2831e65936438b550d7b
- https://github.com/aircrack-ng/aircrack-ng/pull/14
- http://aircrack-ng.blogspot.com/2014/10/aircrack-ng-12-release-candidate-1.html
- https://github.com/aircrack-ng/aircrack-ng/commit/091b153f294b9b695b0b2831e65936438b550d7b
- https://github.com/aircrack-ng/aircrack-ng/pull/14
