# [H] CVE-2017-6088

## Summary
Severity: High
Advisory: CVE-2017-6088
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2017-6088
Type: osv

## Details
Multiple SQL injection vulnerabilities in EyesOfNetwork (aka EON) 5.0 and earlier allow remote authenticated users to execute arbitrary SQL commands via the (1) bp_name, (2) display, (3) search, or (4) equipment parameter to module/monitoring_ged/ged_functions.php or the (5) type parameter to monitoring_ged/ajax.php.

## References
- http://www.securityfocus.com/bid/97084
- http://www.openwall.com/lists/oss-security/2017/03/23/4
- https://sysdream.com/news/lab/2017-03-14-cve-2017-6088-eon-5-0-multiple-sql-injection/
- https://www.exploit-db.com/exploits/41747/
