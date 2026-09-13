# [H] BIT-modsecurity-2023-28882

## Summary
Severity: High
Advisory: BIT-modsecurity-2023-28882
Aliases: BIT-modsecurity2-2023-28882, CVE-2023-28882
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-modsecurity-2023-28882
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.5 <3.0.9

## Details
Trustwave ModSecurity 3.0.5 through 3.0.8 before 3.0.9 allows a denial of service (worker crash and unresponsiveness) because some inputs cause a segfault in the Transaction class for some configurations.

## References
- https://www.trustwave.com/en-us/resources/security-resources/software-updates/announcing-modsecurity-version-309/
- https://nvd.nist.gov/vuln/detail/CVE-2023-28882
