# [M] Apache Hadoop: Temporary File Local Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2024-23454
Aliases: GHSA-f5fw-25gw-5m92
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-25
Source: https://osv.dev/vulnerability/CVE-2024-23454
Type: osv

## Details
Apache Hadoop’s RunJar.run() does not set permissions for temporary directory by default. If sensitive data will be present in this file, all the other local users may be able to view the content.
This is because, on unix-like systems, the system temporary directory is
shared between all local users. As such, files written in this directory,
without setting the correct posix permissions explicitly, may be viewable
by all other local users.

## References
- http://www.openwall.com/lists/oss-security/2024/09/25/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23454.json
- https://lists.apache.org/thread/xlo7q8kn4tsjvx059r789oz19hzgfkfs
- https://nvd.nist.gov/vuln/detail/CVE-2024-23454
- https://security.netapp.com/advisory/ntap-20241101-0002/
- https://issues.apache.org/jira/browse/HADOOP-19031
