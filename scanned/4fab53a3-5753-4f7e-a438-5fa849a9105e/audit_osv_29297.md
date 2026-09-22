# [M] CVE-2024-41434

## Summary
Severity: Medium
Advisory: CVE-2024-41434
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-41434
Type: osv

## Details
PingCAP TiDB v8.1.0 was discovered to contain a buffer overflow via the component (*Column).GetDecimal. This allows attackers to cause a Denial of Service (DoS) via a crafted input to the 'RemoveUnnecessaryFirstRow', it will check the expression between 'Agg' and 'GroupBy', but does not check the return type. NOTE: PingCAP disputes this, arguing that reproduction did not cause the security impact of service interruption to other users. They maintain it is a complex query bug in the product but not a DoS.

## References
- https://gist.github.com/ycybfhb/4aa6809695b9e8a1cd1429e597c17517
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41434.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41434
- https://github.com/pingcap/tidb/issues/53733
