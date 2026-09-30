# [H] Apache ShardingSphere ElasticJob-UI allows RCE via event trace data source JDBC

## Summary
Severity: High
Advisory: CVE-2022-31764
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-06
Source: https://osv.dev/vulnerability/CVE-2022-31764
Type: osv

## Details
The Lite UI of Apache ShardingSphere ElasticJob-UI allows an attacker to perform RCE by constructing a special JDBC URL of H2 database. This issue affects Apache ShardingSphere ElasticJob-UI version 3.0.1 and prior versions. This vulnerability has been fixed in ElasticJob-UI 3.0.2.
The premise of this attack is that the attacker has obtained the account and password. Otherwise, the attacker cannot perform this attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31764.json
- https://lists.apache.org/thread/pg0k223m4hsnnzg4nh7lxvdxxgbkrlqb
- https://nvd.nist.gov/vuln/detail/CVE-2022-31764
