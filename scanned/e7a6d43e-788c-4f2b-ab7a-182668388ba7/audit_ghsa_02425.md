# [H] Unauthenticated SQL Injection in Cachet

## Summary
Severity: High
Advisory: GHSA-79mg-4w23-4fqc
CVE: CVE-2021-39165
CWE: CWE-287, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-79mg-4w23-4fqc
Type: github-advisory

## Affected
- Packagist: `cachethq/cachet` — affected >=0

## Details
### Impact
In Cachet versions through 2.3.18, there is a SQL injection which is in the `SearchableTrait#scopeSearch()`. Attackers without authentication can utilize this vulnerability to exfiltrate sensitive data from the database such as administrator's password and session.

### Patches

The original repository of [https://github.com/CachetHQ/Cachet](https://github.com/CachetHQ/Cachet) is not active, the stable version 2.3.18 and it's developing 2.4 branch is affected. 

Update to version 2.5 or later in the [https://github.com/fiveai/Cachet fork](https://github.com/fiveai/Cachet) to fix this vulnerability.

## References
- https://github.com/fiveai/Cachet/security/advisories/GHSA-79mg-4w23-4fqc
- https://nvd.nist.gov/vuln/detail/CVE-2021-39165
- https://github.com/fiveai/Cachet/commit/27bca8280419966ba80c6fa283d985ddffa84bb6
