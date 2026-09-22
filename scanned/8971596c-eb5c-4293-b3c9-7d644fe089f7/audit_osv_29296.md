# [C] CVE-2024-41433

## Summary
Severity: Critical
Advisory: CVE-2024-41433
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-41433
Type: osv

## Details
PingCAP TiDB v8.1.0 was discovered to contain a buffer overflow via the component expression.ExplainExpressionList. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted input. NOTE: PingCAP maintains that the actual reproduction of this issue did not cause the security impact of service interruption to other users. They argue that this is a complex query bug and not a DoS vulnerability.

## References
- https://gist.github.com/ycybfhb/eec3a1eefe4c85eb22f1bca6114359a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41433.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41433
- https://github.com/pingcap/tidb/issues/53796
