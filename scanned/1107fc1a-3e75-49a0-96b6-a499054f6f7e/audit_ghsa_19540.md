# [H] Vipshop Saturn Console Vulnerable to SQL Injection via ClusterKey Component

## Summary
Severity: High
Advisory: GHSA-49v8-p6mm-3pfj
CVE: CVE-2025-29085
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-49v8-p6mm-3pfj
Type: github-advisory

## Affected
- Maven: `com.vip.saturn:saturn-console` — affected >=0

## Details
SQL injection vulnerability in vipshop Saturn v.3.5.1 and before allows a remote attacker to execute arbitrary code via /console/dashboard/executorCount?zkClusterKey component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29085
- https://gist.github.com/Cafe-Tea/bcef0d7a2bdb5ec8e0d69de852fdc900
- https://github.com/vipshop/Saturn
