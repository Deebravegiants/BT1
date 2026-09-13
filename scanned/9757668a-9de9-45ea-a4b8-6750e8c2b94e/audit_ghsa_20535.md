# [M] Exposure of Sensitive Information to an Unauthorized Actor in Apache NiFi

## Summary
Severity: Medium
Advisory: GHSA-rq96-qhc5-vm4r
CVE: CVE-2021-44145
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-05
Source: https://github.com/advisories/GHSA-rq96-qhc5-vm4r
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=0 <1.15.1

## Details
In the TransformXML processor of Apache NiFi before 1.15.1 an authenticated user could configure an XSLT file which, if it included malicious external entity calls, may reveal sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44145
- https://nifi.apache.org/security.html#1.15.1-vulnerabilities
- http://www.openwall.com/lists/oss-security/2021/12/17/1
