# [H] Apache Jetspeed vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-88f6-79x2-xqf3
CVE: CVE-2016-0710
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-88f6-79x2-xqf3
Type: github-advisory

## Affected
- Maven: `org.apache.portals.jetspeed-2:jetspeed` — affected >=0 <2.3.1

## Details
Multiple SQL injection vulnerabilities in the User Manager service in Apache Jetspeed before 2.3.1 allow remote attackers to execute arbitrary SQL commands via the (1) role or (2) user parameter to services/usermanager/users/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0710
- https://mail-archives.apache.org/mod_mbox/portals-jetspeed-user/201603.mbox/%3C046318A1-226E-453F-9394-B84F1A33E6A4%40bluesunrise.com%3E
- https://mail-archives.apache.org/mod_mbox/portals-jetspeed-user/201603.mbox/%3C046318A1-226E-453F-9394-B84F1A33E6A4@bluesunrise.com%3E
- https://portals.apache.org/jetspeed-2/security-reports.html#CVE-2016-0710
- https://www.exploit-db.com/exploits/39643
- http://haxx.ml/post/140552592371/remote-code-execution-in-apache-jetspeed-230-and
- http://packetstormsecurity.com/files/136489/Apache-Jetspeed-Arbitrary-File-Upload.html
- http://www.rapid7.com/db/modules/exploit/multi/http/apache_jetspeed_file_upload
