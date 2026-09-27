# [M] Apache James MIME4J vulnerable to information disclosure to local users

## Summary
Severity: Medium
Advisory: GHSA-q84x-3476-8ff2
CVE: CVE-2022-45787
CWE: CWE-200, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-q84x-3476-8ff2
Type: github-advisory

## Affected
- Maven: `org.apache.james:apache-mime4j-storage` — affected >=0 <0.8.9

## Details
Unproper laxist permissions on the temporary files used by MIME4J TempFileStorageProvider may lead to information disclosure to other local users. This issue affects Apache James MIME4J version 0.8.8 and prior versions. We recommend users to upgrade to MIME4j version 0.8.9 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45787
- https://github.com/apache/james-mime4j/commit/021eb79ba312fe5a7f99fa867ee5350aa5533069
- https://github.com/apache/james-mime4j
- https://github.com/apache/james-mime4j/blob/master/CHANGELOG.md#089---2022-12-30
- https://issues.apache.org/jira/browse/MIME4J-322
- https://lists.apache.org/thread/26s8p9stl1z261c4qw15bsq03tt7t0rj
