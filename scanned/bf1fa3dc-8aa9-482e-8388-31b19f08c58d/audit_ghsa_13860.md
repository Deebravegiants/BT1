# [H] Apache InLong contains Out-of-bounds Read vulnerability

## Summary
Severity: High
Advisory: GHSA-q9p5-w2v9-6wxf
CVE: CVE-2023-24977
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-q9p5-w2v9-6wxf
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:inlong` — affected >=1.1.0

## Details
Out-of-bounds Read vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.1.0 through 1.5.0. Users are advised to upgrade to Apache InLong's latest version or cherry-pick https://github.com/apache/inlong/pull/7214 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24977
- https://github.com/apache/inlong/pull/7214
- https://github.com/apache/inlong
- https://lists.apache.org/thread/ggozxorctn3tdll7bgmpwwcbjnd0s6w7
