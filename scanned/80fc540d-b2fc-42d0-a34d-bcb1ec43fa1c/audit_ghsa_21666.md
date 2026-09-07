# [H] Apache Geode SSL endpoint verification vulnerability

## Summary
Severity: High
Advisory: GHSA-wc4x-4gm2-74j8
CVE: CVE-2019-10091
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-wc4x-4gm2-74j8
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=0 <1.10.0

## Details
When TLS is enabled with ssl-endpoint-identification-enabled set to true, Apache Geode fails to perform hostname verification of the entries in the certificate SAN during the SSL handshake. This could compromise intra-cluster communication using a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10091
- https://github.com/apache/geode/pull/3849
- https://github.com/apache/geode/commit/e57028fd62a2f5980ea6c9a7ab89ada06c828634
- https://cwiki.apache.org/confluence/display/GEODE/Release+Notes#ReleaseNotes-SecurityVulnerabilities
- https://issues.apache.org/jira/browse/GEODE-7018
- https://lists.apache.org/thread.html/r3342077ac4798631300366be86e545d0c08753cca8fd2663867fe200%40%3Cdev.geode.apache.org%3E
