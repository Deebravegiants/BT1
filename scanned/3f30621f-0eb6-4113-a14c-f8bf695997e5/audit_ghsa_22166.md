# [H] Path Traversal in Apache Jetspeed

## Summary
Severity: High
Advisory: GHSA-w47p-5q88-hj5g
CVE: CVE-2016-0709
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w47p-5q88-hj5g
Type: github-advisory

## Affected
- Maven: `org.apache.portals.jetspeed-2:jetspeed` — affected >=0 <2.3.1

## Details
Directory traversal vulnerability in the Import/Export function in the Portal Site Manager in Apache Jetspeed before 2.3.1 allows remote authenticated administrators to write to arbitrary files, and consequently execute arbitrary code, via a .. (dot dot) in a ZIP archive entry, as demonstrated by "../../webapps/x.jsp."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0709
- https://mail-archives.apache.org/mod_mbox/portals-jetspeed-user/201603.mbox/%3C281D02D0-6A03-4421-9D86-E73B001C8677@bluesunrise.com%3E
- https://portals.apache.org/jetspeed-2/security-reports.html#CVE-2016-0709
- https://www.exploit-db.com/exploits/39643
- http://haxx.ml/post/140552592371/remote-code-execution-in-apache-jetspeed-230-and
- http://packetstormsecurity.com/files/136489/Apache-Jetspeed-Arbitrary-File-Upload.html
- http://www.rapid7.com/db/modules/exploit/multi/http/apache_jetspeed_file_upload
