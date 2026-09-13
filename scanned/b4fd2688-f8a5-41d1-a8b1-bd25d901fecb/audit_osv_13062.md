# [C] CVE-2018-17191

## Summary
Severity: Critical
Advisory: CVE-2018-17191
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-17191
Type: osv

## Details
Apache NetBeans (incubating) 9.0 NetBeans Proxy Auto-Configuration (PAC) interpretation is vulnerable for remote command execution (RCE). Using the nashorn script engine the environment of the javascript execution for the Proxy Auto-Configuration leaks privileged objects, that can be used to circumvent the execution limits. If a different script engine was used, no execution limits were in place. Both vectors allow remote code execution.

## References
- https://lists.apache.org/thread.html/d1c37966a316a326ab4ff4d4bc056322e8adcbe984e8145c0ecda7fa%40%3Cdev.netbeans.apache.org%3E
- http://www.securityfocus.com/bid/106352
