# [C] Deserialization of Untrusted Data in Apache Olingo

## Summary
Severity: Critical
Advisory: GHSA-gj76-429m-56wc
CVE: CVE-2019-17556
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-04
Source: https://github.com/advisories/GHSA-gj76-429m-56wc
Type: github-advisory

## Affected
- Maven: `org.apache.olingo:odata-client-proxy` — affected >=4.0.0 <4.7.0

## Details
Apache Olingo versions 4.0.0 to 4.6.0 provide the AbstractService class, which is public API, uses ObjectInputStream and doesn't check classes being deserialized. If an attacker can feed malicious metadata to the class, then it may result in running attacker's code in the worse case.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17556
- https://github.com/apache/olingo-odata4/pull/60/files
- https://issues.apache.org/jira/browse/OLINGO-1410
- https://mail-archives.apache.org/mod_mbox/olingo-user/201912.mbox/%3CCAGSZ4d4vbSYaVh3aUWAvcVHK2qcFxxCZd3WAx3xbwZXskPX8nw%40mail.gmail.com%3E
