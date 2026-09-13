# [H] CVE-2015-8604

## Summary
Severity: High
Advisory: CVE-2015-8604
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-11
Source: https://osv.dev/vulnerability/CVE-2015-8604
Type: osv

## Details
SQL injection vulnerability in the host_new_graphs function in graphs_new.php in Cacti 0.8.8f and earlier allows remote authenticated users to execute arbitrary SQL commands via the cg_g parameter in a save action.

## References
- http://www.debian.org/security/2016/dsa-3494
- https://security.gentoo.org/glsa/201607-05
- http://bugs.cacti.net/view.php?id=2652
- http://packetstormsecurity.com/files/135191/Cacti-0.8.8f-graphs_new.php-SQL-Injection.html
- http://seclists.org/fulldisclosure/2016/Jan/16
- http://www.openwall.com/lists/oss-security/2016/01/04/8
- http://www.openwall.com/lists/oss-security/2016/01/04/9
- http://www.securitytracker.com/id/1034573
