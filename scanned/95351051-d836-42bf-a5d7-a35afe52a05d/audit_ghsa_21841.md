# [H] Arbitrary code execution in Apache ServiceComb java-chassis

## Summary
Severity: High
Advisory: GHSA-px4w-rcv2-6x8x
CVE: CVE-2020-17532
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-px4w-rcv2-6x8x
Type: github-advisory

## Affected
- Maven: `org.apache.servicecomb:java-chassis` — affected >=1.0.0 <1.3.2
- Maven: `org.apache.servicecomb:java-chassis` — affected >=2.0.0 <2.1.5

## Details
When handler-router component is enabled in servicecomb-java-chassis, authenticated user may inject some data and cause arbitrary code execution.
The problem happens in versions between 2.0.0 ~ 2.1.3 and fixed in Apache ServiceComb-Java-Chassis 2.1.5

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17532
- https://github.com/apache/servicecomb-java-chassis/commit/839a52e27c754cb5ce14f20063902f21065bd26c
- https://github.com/apache/servicecomb-java-chassis/commit/ba4fb37b6ab8bd3a6c3d0693f295d99a94879838
- https://issues.apache.org/jira/browse/SCB-2145
- https://seclists.org/oss-sec/2021/q1/60
