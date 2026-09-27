# [C] CVE-2016-6793

## Summary
Severity: Critical
Advisory: CVE-2016-6793
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2016-6793
Type: osv

## Details
The DiskFileItem class in Apache Wicket 6.x before 6.25.0 and 1.5.x before 1.5.17 allows remote attackers to cause a denial of service (infinite loop) and write to, move, and delete files with the permissions of DiskFileItem, and if running on a Java VM before 1.3.1, execute arbitrary code via a crafted serialized Java object.

## References
- http://www.openwall.com/lists/oss-security/2016/12/31/1
- http://www.securityfocus.com/archive/1/539975/100/0/threaded
- http://www.securityfocus.com/bid/95168
- http://www.securitytracker.com/id/1037541
- https://wicket.apache.org/news/2016/12/31/cve-2016-6793.html
- https://www.tenable.com/security/research/tra-2016-23
