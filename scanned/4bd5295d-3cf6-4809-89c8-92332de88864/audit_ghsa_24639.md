# [H] Arbitrary file write in Apache Commons Fileupload

## Summary
Severity: High
Advisory: GHSA-qx6h-9567-5fqw
CVE: CVE-2013-2186
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qx6h-9567-5fqw
Type: github-advisory

## Affected
- Maven: `commons-fileupload:commons-fileupload` — affected >=0 <1.3.1

## Details
The DiskFileItem class in Apache Commons FileUpload, as used in Red Hat JBoss BRMS 5.3.1; JBoss Portal 4.3 CP07, 5.2.2, and 6.0.0; and Red Hat JBoss Web Server 1.0.2 allows remote attackers to write to arbitrary files via a NULL byte in a file name in a serialized instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2186
- https://github.com/apache/commons-fileupload/commit/163a6061fbc077d4b6e4787d26857c2baba495d1
- https://access.redhat.com/errata/RHSA-2016:0070
- https://exchange.xforce.ibmcloud.com/vulnerabilities/88133
- https://github.com/apache/commons-fileupload
- https://github.com/apache/commons-fileupload/blob/master/RELEASE-NOTES.txt
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-01
- https://www.tenable.com/security/research/tra-2016-23
- http://lists.opensuse.org/opensuse-security-announce/2013-11/msg00008.html
- http://lists.opensuse.org/opensuse-updates/2013-10/msg00033.html
- http://lists.opensuse.org/opensuse-updates/2013-10/msg00050.html
- http://rhn.redhat.com/errata/RHSA-2013-1448.html
- http://ubuntu.com/usn/usn-2029-1
- http://www.debian.org/security/2013/dsa-2827
- http://www.securityfocus.com/bid/63174
