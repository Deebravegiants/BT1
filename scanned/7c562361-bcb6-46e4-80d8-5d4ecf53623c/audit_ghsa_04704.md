# [H] Apache Fluss: Unauthenticated remote attackers can exhaust JVM heap memory using crafted frame headers via TabletServer/CoordinatorServer

## Summary
Severity: High
Advisory: GHSA-4c39-fwgj-4vq7
CVE: CVE-2026-49361
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-4c39-fwgj-4vq7
Type: github-advisory

## Affected
- Maven: `org.apache.fluss:fluss-common` — affected >=0.8.0-incubating-rc1 <0.9.1-incubating

## Details
Apache Fluss versions prior to 0.9.1 configure the Netty LengthFieldBasedFrameDecoder with Integer.MAX_VALUE as the maximum frame length, allowing unauthenticated remote attackers to exhaust JVM heap memory on TabletServer and CoordinatorServer by sending specially crafted frame headers, resulting in denial of service.

This issue affects Apache Fluss (incubating): 0.8.0 and 0.9.0.

Users are recommended to upgrade to version 0.9.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49361
- https://github.com/apache/fluss
- https://github.com/apache/fluss/releases/tag/v0.9.1-incubating
- https://lists.apache.org/thread/dccw6tj0njwtmvbftq13mw7fdhsok373
- http://www.openwall.com/lists/oss-security/2026/05/30/5
