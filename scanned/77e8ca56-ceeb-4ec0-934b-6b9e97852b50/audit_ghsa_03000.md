# [C] Improper Privilege Management in Apache Ozone

## Summary
Severity: Critical
Advisory: GHSA-86fh-j58m-7pf5
CVE: CVE-2021-36372
CWE: CWE-273
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-86fh-j58m-7pf5
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone-main` — affected >=0 <1.2.0

## Details
In Apache Ozone versions prior to 1.2.0, Initially generated block tokens are persisted to the metadata database and can be retrieved with authenticated users with permission to the key. Authenticated users may use them even after access is revoked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36372
- https://github.com/apache/ozone
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3C5029c1ac-4685-8492-e3cb-ab48c5c370cf%40apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/19/1
