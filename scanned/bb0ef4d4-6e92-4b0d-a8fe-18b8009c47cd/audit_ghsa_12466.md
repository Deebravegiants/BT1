# [C] Apache IoTDB: Unsafe deserialize map in Sync Tool

## Summary
Severity: Critical
Advisory: GHSA-f23h-52hj-99p6
CVE: CVE-2023-51656
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-f23h-52hj-99p6
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-parent` — affected >=0.13.0 <1.2.2

## Details
Deserialization of Untrusted Data vulnerability in Apache IoTDB.This issue affects Apache IoTDB: from 0.13.0 through 0.13.4.

Users are recommended to upgrade to version 1.2.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51656
- https://github.com/apache/iotdb
- https://lists.apache.org/thread/zy3klwpv11vl5n65josbfo2fyzxg3dxc
- http://www.openwall.com/lists/oss-security/2023/12/21/5
