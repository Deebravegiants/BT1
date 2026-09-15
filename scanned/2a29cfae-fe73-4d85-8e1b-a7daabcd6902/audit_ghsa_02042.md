# [M] Improper Check for Unusual or Exceptional Conditions in json-smart

## Summary
Severity: Medium
Advisory: GHSA-v528-7hrm-frqp
CVE: CVE-2021-27568
CWE: CWE-754
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-v528-7hrm-frqp
Type: github-advisory

## Affected
- Maven: `net.minidev:json-smart` — affected >=0 <1.3.2
- Maven: `net.minidev:json-smart` — affected >=2.4.0 <2.4.1
- Maven: `net.minidev:json-smart-mini` — affected >=0 <1.3.2
- Maven: `net.minidev:json-smart` — affected >=2.0.0 <2.3.1

## Details
An issue was discovered in netplex json-smart-v1 through 2015-10-23 and json-smart-v2 through 2.4. An exception is thrown from a function, but it is not caught, as demonstrated by NumberFormatException. When it is not caught, it may cause programs using the library to crash or expose sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27568
- https://github.com/netplex/json-smart-v1/issues/7
- https://github.com/netplex/json-smart-v2/issues/60
- https://github.com/netplex/json-smart-v2/issues/62
- https://github.com/netplex/json-smart-v2/pull/72
- https://github.com/netplex/json-smart-v1/commit/768db58ee0e3e344fcdb574b7629765308a1d0af
- https://github.com/netplex/json-smart-v2
- https://lists.apache.org/thread.html/rb6287f5aa628c8d9af52b5401ec6cc51b6fc28ab20d318943453e396@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/re237267da268c690df5e1c6ea6a38a7fc11617725e8049490f58a6fa@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rf70210b4d63191c0bfb2a0d5745e104484e71703bf5ad9cb01c980c6@%3Ccommits.druid.apache.org%3E
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
