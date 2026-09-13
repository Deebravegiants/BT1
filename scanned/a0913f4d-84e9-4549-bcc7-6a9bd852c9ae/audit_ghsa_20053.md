# [M] Apache Commons Net vulnerable to information leakage via malicious server

## Summary
Severity: Medium
Advisory: GHSA-cgp8-4m63-fhh5
CVE: CVE-2021-37533
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-03
Source: https://github.com/advisories/GHSA-cgp8-4m63-fhh5
Type: github-advisory

## Affected
- Maven: `commons-net:commons-net` — affected >=0 <3.9.0

## Details
Prior to Apache Commons Net 3.9.0, Net's FTP client trusts the host from PASV response by default. A malicious server can redirect the Commons Net code to use a different host, but the user has to connect to the malicious server in the first place. This may lead to leakage of information about services running on the private network of the client.
The default in version 3.9.0 is now false to ignore such hosts, as cURL does. See https://issues.apache.org/jira/browse/NET-711.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37533
- https://github.com/apache/commons-net/commit/4fe1bae56e53f32756b1ca3296f3dd2c45e3e060
- https://github.com/apache/commons-net
- https://issues.apache.org/jira/browse/NET-711
- https://lists.apache.org/thread/o6yn9r9x6s94v97264hmgol1sf48mvx7
- https://lists.debian.org/debian-lts-announce/2022/12/msg00038.html
- https://www.debian.org/security/2022/dsa-5307
- http://www.openwall.com/lists/oss-security/2022/12/03/1
