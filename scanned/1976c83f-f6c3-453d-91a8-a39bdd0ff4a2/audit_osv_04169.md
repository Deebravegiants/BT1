# [H] BIT-appsmith-2024-51408

## Summary
Severity: High
Advisory: BIT-appsmith-2024-51408
Aliases: CVE-2024-51408
Ecosystem: Bitnami
Published: 2024-11-07
Source: https://osv.dev/vulnerability/BIT-appsmith-2024-51408
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=1.8.3 <1.46.0

## Details
AppSmith Community 1.8.3 before 1.46 allows SSRF via New DataSource for application/json requests to 169.254.169.254 to retrieve AWS metadata credentials.

## References
- https://github.com/appsmithorg/appsmith/pull/29286
- https://github.com/appsmithorg/appsmith/releases/tag/v1.46
- https://github.com/jahithoque/Vulnerability-Research/tree/main/CVE-2024-51408
- https://nvd.nist.gov/vuln/detail/CVE-2024-51408
