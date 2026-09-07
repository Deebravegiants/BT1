# [H] Apache HugeGraph-Server: Bypass whitelist in Auth mode

## Summary
Severity: High
Advisory: GHSA-6mgp-p75r-vhjm
CVE: CVE-2024-27349
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-6mgp-p75r-vhjm
Type: github-advisory

## Affected
- Maven: `org.apache.hugegraph:hugegraph-api` — affected >=1.0.0 <1.3.0

## Details
Authentication Bypass by Spoofing vulnerability in Apache HugeGraph-Server.This issue affects Apache HugeGraph-Server: from 1.0.0 before 1.3.0.

Users are recommended to upgrade to version 1.3.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27349
- https://github.com/apache/incubator-hugegraph/commit/713d88d1fd9953c3c3e3f130389501910ba40e1d
- https://github.com/apache/incubator-hugegraph
- https://lists.apache.org/thread/dz9n9lndqfsf64t72o73r7sttrc6ocsd
- http://www.openwall.com/lists/oss-security/2024/04/22/4
