# [C] Grafana Command Injection And Local File Inclusion Via Sql Expressions

## Summary
Severity: Critical
Advisory: GHSA-q99m-qcv4-fpm7
CVE: CVE-2024-9264
CWE: CWE-77, CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-18
Source: https://github.com/advisories/GHSA-q99m-qcv4-fpm7
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=11.0.0 <11.0.6+security-01
- Go: `github.com/grafana/grafana` — affected >=11.1.0 <11.1.7+security-01
- Go: `github.com/grafana/grafana` — affected >=11.2.0 <11.2.2+security-01

## Details
The SQL Expressions experimental feature of Grafana allows for the evaluation of `duckdb` queries containing user input. These queries are insufficiently sanitized before being passed to `duckdb`, leading to a command injection and local file inclusion vulnerability. Any user with the VIEWER or higher permission is capable of executing this attack.  The `duckdb` binary must be present in Grafana's $PATH for this attack to function; by default, this binary is not installed in Grafana distributions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9264
- https://github.com/grafana/grafana/pull/81666
- https://github.com/grafana/grafana
- https://grafana.com/blog/2024/10/17/grafana-security-release-critical-severity-fix-for-cve-2024-9264
- https://grafana.com/security/security-advisories/cve-2024-9264
- https://security.netapp.com/advisory/ntap-20250314-0007
