# [H] CVE-2016-4338

## Summary
Severity: High
Advisory: CVE-2016-4338
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-4338
Type: osv

## Details
The mysql user parameter configuration script (userparameter_mysql.conf) in the agent in Zabbix before 2.0.18, 2.2.x before 2.2.13, and 3.0.x before 3.0.3, when used with a shell other than bash, allows context-dependent attackers to execute arbitrary code or SQL commands via the mysql.size parameter.

## References
- http://www.securityfocus.com/archive/1/538258/100/0/threaded
- https://www.zabbix.com/documentation/2.0/manual/introduction/whatsnew2018#miscellaneous_improvements
- https://www.zabbix.com/documentation/2.2/manual/introduction/whatsnew2213#miscellaneous_improvements
- https://security.gentoo.org/glsa/201612-42
- https://www.zabbix.com/documentation/3.0/manual/introduction/whatsnew303#miscellaneous_improvements
- http://www.securityfocus.com/bid/89631
- https://support.zabbix.com/browse/ZBX-10741
- http://seclists.org/fulldisclosure/2016/May/9
- https://www.exploit-db.com/exploits/39769/
- http://packetstormsecurity.com/files/136898/Zabbix-Agent-3.0.1-mysql.size-Shell-Command-Injection.html
