# [M] Apache Johnzon Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-crqg-jrpj-fc84
CVE: CVE-2023-33008
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-07-07
Source: https://github.com/advisories/GHSA-crqg-jrpj-fc84
Type: github-advisory

## Affected
- Maven: `org.apache.johnzon:johnzon-mapper` — affected >=0 <1.2.21

## Details
A malicious attacker can craft up some JSON input that uses large numbers (numbers such as 1e20000000) that Apache Johnzon will deserialize into BigDecimal and maybe use numbers too large which may result in a slow conversion (Denial of service risk). Apache Johnzon 1.2.21 mitigates this by setting a scale limit of 1000 (by default) to the BigDecimal. 


This issue affects Apache Johnzon through 1.2.20.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33008
- https://github.com/apache/johnzon/commit/34ad9a6b296ae7b4667c3cf0037998e451499ea4
- https://github.com/apache/johnzon
- https://issues.apache.org/jira/browse/JOHNZON-397
- https://lists.apache.org/thread/qbg14djo95gfpk7o560lr8wcrzfyw43l
