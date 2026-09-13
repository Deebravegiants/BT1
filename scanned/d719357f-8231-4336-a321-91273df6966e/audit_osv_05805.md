# [M] BIT-haproxy-2026-26081

## Summary
Severity: Medium
Advisory: BIT-haproxy-2026-26081
Aliases: CVE-2026-26081
Ecosystem: Bitnami
Published: 2026-08-26
Source: https://osv.dev/vulnerability/BIT-haproxy-2026-26081
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=3.3.0 <3.3.3

## Details
HAProxy Community Edition 3.0 through 3.3 before 3.3.3 lacks a length check for the NEW_TOKEN format. HAProxy Enterprise and ALOHA are also affected.

## References
- https://git.haproxy.org/?p=haproxy-3.2.git;a=commit;h=4765277f4f915baac2d57db63538ff0a59966deb
- https://nvd.nist.gov/vuln/detail/CVE-2026-26081
- https://www.haproxy.org
