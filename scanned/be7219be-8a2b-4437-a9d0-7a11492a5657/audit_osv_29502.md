# [H] CVE-2024-43199

## Summary
Severity: High
Advisory: CVE-2024-43199
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-43199
Type: osv

## Details
Nagios NDOUtils before 2.1.4 allows privilege escalation from nagios to root because certain executable files are owned by the nagios user.

## References
- http://www.openwall.com/lists/oss-security/2024/08/14/8
- https://github.com/NagiosEnterprises/ndoutils/compare/ndoutils-2.1.3...ndoutils-2.1.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43199.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43199
- https://github.com/NagiosEnterprises/ndoutils/commit/18ef12037f4a68772d6840cbaa08aa2da07d2891
- https://github.com/NagiosEnterprises/ndoutils/pull/65
