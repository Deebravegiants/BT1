# [H] Apache ShenYu Admin has insecure permissions

## Summary
Severity: High
Advisory: GHSA-fjjw-82xw-vfc2
CVE: CVE-2022-37435
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-02
Source: https://github.com/advisories/GHSA-fjjw-82xw-vfc2
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu-common` — affected >=2.4.2 <2.5.0

## Details
Apache ShenYu Admin has insecure permissions, which may allow low-privilege administrators to modify high-privilege administrator's passwords. This issue affects Apache ShenYu 2.4.2 and 2.4.3. Version 2.5.0 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37435
- https://github.com/apache/shenyu/pull/3658
- https://github.com/apache/shenyu/releases/tag/v2.5.0
- https://lists.apache.org/thread/ndblyxr2fdrvjtgbs1bogxgv2cgk7t28
