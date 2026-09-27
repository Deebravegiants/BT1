# [H] BIT-redash-2020-12725

## Summary
Severity: High
Advisory: BIT-redash-2020-12725
Aliases: CVE-2020-12725
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redash-2020-12725
Type: osv

## Affected
- Bitnami: `redash` — affected >=0 <8.0.0

## Details
Havoc Research discovered an authenticated Server-Side Request Forgery (SSRF) via the "JSON" data source of Redash open-source 8.0.0 and prior. Possibly, other connectors are affected. The SSRF is potent and provides a lot of flexibility in terms of being able to craft HTTP requests e.g., by adding headers, selecting any HTTP verb, etc.

## References
- https://blog.redash.io
- https://github.com/getredash/redash/commits/master
- https://github.com/getredash/redash/issues/4869
