# [M] Apache Axis2 has Improper Input Validation

## Summary
Severity: Medium
Advisory: GHSA-wwq7-pxwc-p4rc
CVE: CVE-2012-5785
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wwq7-pxwc-p4rc
Type: github-advisory

## Affected
- Maven: `org.apache.axis2:axis2` — affected >=0 <1.8.0
- Maven: `org.apache.axis2:axis2-transport-http` — affected >=0 <1.8.0

## Details
Apache Axis2/Java 1.7.9 and earlier does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5785
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79830
- https://github.com/apache/axis-axis2-java-core
- https://issues.apache.org/jira/browse/AXIS2-6018
- http://www.cs.utexas.edu/~shmat/shmat_ccs12.pdf
