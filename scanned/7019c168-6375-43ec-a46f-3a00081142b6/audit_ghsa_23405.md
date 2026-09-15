# [H] Apache Libcloud does not verify SSL certificates for HTTPS connections

## Summary
Severity: High
Advisory: GHSA-w3j6-8j34-q43x
CVE: CVE-2010-4340
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w3j6-8j34-q43x
Type: github-advisory

## Affected
- PyPI: `apache-libcloud` — affected >=0 <0.4.0

## Details
libcloud before 0.4.0 does not verify SSL certificates for HTTPS connections, which allows remote attackers to spoof certificates and bypass intended access restrictions via a man-in-the-middle (MITM) attack. This is due to an upstream issue with python's SSL module rather than directly with libcloud.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4340
- https://github.com/apache/libcloud/commit/87ee61e6ba03a43dcefea2ce180988bec066b6fd
- https://bugs.python.org/issue1589
- https://github.com/apache/libcloud
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-libcloud/PYSEC-2011-24.yaml
- https://issues.apache.org/jira/browse/LIBCLOUD-55
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=598463
- http://mail-archives.apache.org/mod_mbox/incubator-libcloud/201009.mbox/%3C5860913.463891285776633273.JavaMail.jira@thor%3E
- http://mail-archives.apache.org/mod_mbox/incubator-libcloud/201011.mbox/browser
- http://wiki.apache.org/incubator/LibcloudSSL
