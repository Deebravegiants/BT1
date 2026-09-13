# [H] BIT-appsmith-2022-38298

## Summary
Severity: High
Advisory: BIT-appsmith-2022-38298
Aliases: CVE-2022-38298
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-appsmith-2022-38298
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=1.7.11 <1.7.12

## Details
Appsmith v1.7.11 was discovered to allow attackers to execute an authenticated Server-Side Request Forgery (SSRF) via redirecting incoming requests to the AWS internal metadata endpoint.

## References
- https://github.com/appsmithorg/appsmith/pull/15782
- https://nvd.nist.gov/vuln/detail/CVE-2022-38298
