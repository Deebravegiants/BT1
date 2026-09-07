# [M] Incorrect permissions in Apache Ozone

## Summary
Severity: Medium
Advisory: GHSA-c6j7-4fr9-c76p
CVE: CVE-2021-39235
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-c6j7-4fr9-c76p
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone-main` — affected >=0 <1.2.0

## Details
In Apache Ozone before 1.2.0, Ozone Datanode doesn't check the access mode parameter of the block token. Authenticated users with valid READ block token can do any write operation on the same block.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39235
- https://github.com/apache/ozone
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3C93f88246-4320-7423-0dac-ec7a07f47455%40apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/19/6
