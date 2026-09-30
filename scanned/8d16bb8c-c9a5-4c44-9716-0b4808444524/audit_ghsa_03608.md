# [M] Apache NiFi information disclosure by XXE

## Summary
Severity: Medium
Advisory: GHSA-744r-vv2g-2x6g
CVE: CVE-2019-10080
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-744r-vv2g-2x6g
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-security` — affected >=1.3.0 <1.10.0
- Maven: `org.apache.nifi:nifi` — affected >=1.3.0 <1.10.0

## Details
The XMLFileLookupService in NiFi versions 1.3.0 to 1.9.2 allowed trusted users to inadvertently configure a potentially malicious XML file. The XML file has the ability to make external calls to services (via XXE) and reveal information such as the versions of Java, Jersey, and Apache that the NiFI instance uses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10080
- https://github.com/apache/nifi/pull/3507
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://nifi.apache.org/security.html#CVE-2019-10080
- https://www.oracle.com/security-alerts/cpuApr2021.html
