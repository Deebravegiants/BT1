# [C] Path traversal in Apache James

## Summary
Severity: Critical
Advisory: GHSA-c38m-7h53-g9v4
CVE: CVE-2021-40525
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-c38m-7h53-g9v4
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0 <3.6.1

## Details
Apache James ManagedSieve implementation alongside with the file storage for sieve scripts is vulnerable to path traversal, allowing reading and writing any file. This vulnerability had been patched in Apache James 3.6.1 and higher. We recommend the upgrade. Distributed and Cassandra based products are also not impacted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40525
- https://github.com/apache/james-project
- https://www.openwall.com/lists/oss-security/2022/01/04/4
- http://www.openwall.com/lists/oss-security/2022/01/04/4
- http://www.openwall.com/lists/oss-security/2022/02/07/1
