# [C] Apache ShardingSphere-Proxy Incomplete Cleanup vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wmxm-6wxc-3xqf
CVE: CVE-2022-45347
CWE: CWE-459
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-wmxm-6wxc-3xqf
Type: github-advisory

## Affected
- Maven: `org.apache.shardingsphere:shardingsphere-proxy` — affected >=0 <5.3.0

## Details
Apache ShardingSphere-Proxy prior to 5.3.0 when using MySQL as database backend didn't cleanup the database session completely after client authentication failed, which allowed an attacker to execute normal commands by constructing a special MySQL client. This vulnerability has been fixed in Apache ShardingSphere 5.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45347
- https://github.com/pjfanning/shardingsphere
- https://lists.apache.org/thread/l5rz7j4rg10o7ywtgknh2f5hxnv6yw3l
