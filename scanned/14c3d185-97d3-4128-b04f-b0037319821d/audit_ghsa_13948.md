# [H] Privilege escalation in Apache ShenYu

## Summary
Severity: High
Advisory: GHSA-vf8h-2wwj-jq22
CVE: CVE-2022-42735
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-vf8h-2wwj-jq22
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu-admin` — affected >=0 <2.5.1

## Details
Improper Privilege Management vulnerability in Apache Software Foundation Apache ShenYu. ShenYu Admin allows low-privilege low-level administrators create users with higher privileges than their own. This issue affects Apache ShenYu: 2.5.0. Upgrade to Apache ShenYu 2.5.1 or apply patch https://github.com/apache/shenyu/pull/3958.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42735
- https://github.com/apache/shenyu/pull/3958
- https://github.com/apache/shenyu
- https://lists.apache.org/thread/2k8764jmckmc19qc8x51nlnngq71pcf7
