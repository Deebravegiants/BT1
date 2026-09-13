# [C] BIT-json-c-2021-32292

## Summary
Severity: Critical
Advisory: BIT-json-c-2021-32292
Aliases: CVE-2021-32292
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-json-c-2021-32292
Type: osv

## Affected
- Bitnami: `json-c` — affected >=0.15-20200726.0

## Details
An issue was discovered in json-c from 20200420 (post 0.14 unreleased code) through 0.15-20200726. A stack-buffer-overflow exists in the auxiliary sample program json_parse which is located in the function parseit.

## References
- https://github.com/json-c/json-c/issues/654
- https://security.netapp.com/advisory/ntap-20230929-0010/
- https://www.debian.org/security/2023/dsa-5486
