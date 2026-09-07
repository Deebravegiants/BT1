# [C] Arbitrary code execution in clickhouse-driver

## Summary
Severity: Critical
Advisory: GHSA-vgv5-cxvh-vfxh
CVE: CVE-2020-26759
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-vgv5-cxvh-vfxh
Type: github-advisory

## Affected
- PyPI: `clickhouse-driver` — affected >=0 <0.1.5

## Details
clickhouse-driver before 0.1.5 allows a malicious clickhouse server to trigger a crash or execute arbitrary code (on a database client) via a crafted server response, due to a buffer overflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26759
- https://github.com/mymarilyn/clickhouse-driver/commit/3e990547e064b8fca916b23a0f7d6fe8c63c7f6b
- https://github.com/mymarilyn/clickhouse-driver/commit/d708ed548e1d6f254ba81a21de8ba543a53b5598
- https://github.com/advisories/GHSA-vgv5-cxvh-vfxh
- https://github.com/mymarilyn/clickhouse-driver
- https://github.com/pypa/advisory-database/tree/main/vulns/clickhouse-driver/PYSEC-2021-61.yaml
