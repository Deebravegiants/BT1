# [H] CVE-2013-6876

## Summary
Severity: High
Advisory: CVE-2013-6876
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-06
Source: https://osv.dev/vulnerability/CVE-2013-6876
Type: osv

## Details
The (1) pty_init_terminal and (2) pipe_init_terminal functions in main.c in s3dvt 0.2.2 and earlier allows local users to gain privileges by leveraging setuid permissions and usage of bash 4.3 and earlier.  NOTE: this vulnerability was fixed with commit ad732f00b411b092c66a04c359da0f16ec3b387, but the version number was not changed.

## References
- http://hmarco.org/bugs/s3dvt_0.2.2-root-shell.html
- http://packetstormsecurity.com/files/126887/s3dvt-Privilege-Escalation.html
- http://seclists.org/fulldisclosure/2014/Jun/10
- http://www.openwall.com/lists/oss-security/2014/06/03/11
- http://www.securityfocus.com/bid/67789
- http://seclists.org/fulldisclosure/2014/Jun/10
- http://www.openwall.com/lists/oss-security/2014/06/03/11
- http://www.securityfocus.com/archive/1/532258/100/0/threaded
- http://www.securityfocus.com/archive/1/532276/100/0/threaded
