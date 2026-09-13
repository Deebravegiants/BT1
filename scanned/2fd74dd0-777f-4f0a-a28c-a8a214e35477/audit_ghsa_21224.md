# [H] Apache Calcite Avatica JDBC driver arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-w7f5-jrpr-5c2m
CVE: CVE-2022-36364
CWE: CWE-665
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-w7f5-jrpr-5c2m
Type: github-advisory

## Affected
- Maven: `org.apache.calcite.avatica:avatica-core` — affected >=0 <1.22.0

## Details
Apache Calcite Avatica JDBC driver creates HTTP client instances based on class names provided via `httpclient_impl` connection property; however, the driver does not verify if the class implements the expected interface before instantiating it, which can lead to code execution loaded via arbitrary classes and in rare cases remote code execution. To exploit the vulnerability: 1) the attacker needs to have privileges to control JDBC connection parameters; 2) and there should be a vulnerable class (constructor with URL parameter and ability to execute code) in the classpath. From Apache Calcite Avatica 1.22.0 onwards, it will be verified that the class implements the expected interface before invoking its constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36364
- https://github.com/apache/calcite-avatica/commit/0c097b6a685fc1f97f151505a219976f15ed0c4c
- https://github.com/apache/calcite-avatica
- https://lists.apache.org/thread/5csdj8bv4h3hfgw27okm84jh1j2fyw0c
- http://www.openwall.com/lists/oss-security/2022/07/28/1
