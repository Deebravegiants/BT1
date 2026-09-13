# [H] BIT-appsmith-2022-39824

## Summary
Severity: High
Advisory: BIT-appsmith-2022-39824
Aliases: CVE-2022-39824
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-appsmith-2022-39824
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.7.15

## Details
Server-side JavaScript injection in Appsmith through 1.7.14 allows remote attackers to execute arbitrary JavaScript code from the server via the currentItem property of the list widget, e.g., to perform DoS attacks or achieve an information leak.

## References
- https://github.com/FCncdn/Appsmith-Js-Injection-POC
- https://github.com/appsmithorg/appsmith/releases
- https://nvd.nist.gov/vuln/detail/CVE-2022-39824
