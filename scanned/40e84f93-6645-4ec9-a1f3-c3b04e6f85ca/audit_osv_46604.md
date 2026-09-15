# [H] CVE-2014-1226

## Summary
Severity: High
Advisory: CVE-2014-1226
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-06
Source: https://osv.dev/vulnerability/CVE-2014-1226
Type: osv

## Details
The pipe_init_terminal function in main.c in s3dvt allows local users to gain privileges by leveraging setuid permissions and usage of bash 4.3 and earlier.  NOTE: This vulnerability exists because of an incomplete fix for CVE-2013-6876.

## References
- http://hmarco.org/bugs/CVE-2014-1226-s3dvt_0.2.2-root-shell.html
- http://seclists.org/fulldisclosure/2014/Jun/12
- http://www.openwall.com/lists/oss-security/2014/06/03/13
- http://seclists.org/fulldisclosure/2014/Jun/12
- http://www.openwall.com/lists/oss-security/2014/06/03/13
- http://www.securityfocus.com/archive/1/532278/100/0/threaded
