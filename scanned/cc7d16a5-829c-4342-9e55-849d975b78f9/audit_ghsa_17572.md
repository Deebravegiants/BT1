# [H] Apache Commons FileUpload, Apache Commons FileUpload: FileUpload DoS via part headers

## Summary
Severity: High
Advisory: GHSA-vv7r-c36w-3prj
CVE: CVE-2025-48976
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-vv7r-c36w-3prj
Type: github-advisory

## Affected
- Maven: `commons-fileupload:commons-fileupload` — affected >=1.0 <1.6.0
- Maven: `org.apache.commons:commons-fileupload2-core` — affected >=2.0.0-M1 <2.0.0-M4

## Details
Allocation of resources for multipart headers with insufficient limits enabled a DoS vulnerability in Apache Commons FileUpload.

This issue affects Apache Commons FileUpload: from 1.0 before 1.6; from 2.0.0-M1 before 2.0.0-M4.

Users are recommended to upgrade to versions 1.6 or 2.0.0-M4, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48976
- https://github.com/apache/commons-fileupload/commit/b247774a72a044f5d5380ae947140ee80af4e78b
- https://github.com/apache/commons-fileupload/commit/bf68f63cfb312ef4710fb3dfb4d8e4e1665f4497
- https://github.com/apache/tomcat/commit/97790a35a27d236fa053e660676c3f8196284d93
- https://github.com/apache/commons-fileupload
- https://lists.apache.org/thread/fbs3wrr3p67vkjcxogqqqqz45pqtso12
- https://lists.debian.org/debian-lts-announce/2025/07/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- http://www.openwall.com/lists/oss-security/2025/06/16/4
