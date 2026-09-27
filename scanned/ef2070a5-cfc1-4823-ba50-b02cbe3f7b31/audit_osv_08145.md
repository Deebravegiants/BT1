# [H] CVE-2016-10709

## Summary
Severity: High
Advisory: CVE-2016-10709
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-22
Source: https://osv.dev/vulnerability/CVE-2016-10709
Type: osv

## Details
pfSense before 2.3 allows remote authenticated users to execute arbitrary OS commands via a '|' character in the status_rrd_graph_img.php graph parameter, related to _rrd_graph_img.php.

## References
- https://www.pfsense.org/security/advisories/pfSense-SA-16_01.webgui.asc
- https://www.exploit-db.com/exploits/39709/
- https://www.rapid7.com/db/modules/exploit/unix/http/pfsense_graph_injection_exec
- https://www.security-assessment.com/files/documents/advisory/pfsenseAdvisory.pdf
