# [M] Apache Submarine Commons Utils has a hard-coded secret

## Summary
Severity: Medium
Advisory: GHSA-jwcg-wv5x-vg3g
CVE: CVE-2024-36264
CWE: CWE-287, CWE-798
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-12
Source: https://github.com/advisories/GHSA-jwcg-wv5x-vg3g
Type: github-advisory

## Affected
- Maven: `org.apache.submarine:submarine-commons-utils` — affected >=0
- PyPI: `apache-submarine` — affected >=0.8.0

## Details
Improper Authentication vulnerability in Apache Submarine Commons Utils.

This issue affects Apache Submarine Commons Utils: from 0.8.0.

As this project is retired, we do not plan to release a version that fixes this issue. If the user doesn't explicitly set `submarine.auth.default.secret`, a default value will be used. Users are recommended to find an alternative or restrict access to the instance to trusted users. 

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36264
- https://github.com/apache/submarine/pull/1125
- https://github.com/apache/submarine/commit/7a1d551798c6785fc68fe028fc46f74c3ee6976d
- https://github.com/apache/submarine
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-submarine/PYSEC-2024-97.yaml
- https://issues.apache.org/jira/browse/SUBMARINE-1417
- https://lists.apache.org/thread/7mo0c7vbhpo8thvybl8wwvb0bccrg7r4
- http://www.openwall.com/lists/oss-security/2024/06/12/2
