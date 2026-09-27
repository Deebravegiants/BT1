# [H] BIT-varnish-2022-38150

## Summary
Severity: High
Advisory: BIT-varnish-2022-38150
Aliases: CVE-2022-38150
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-varnish-2022-38150
Type: osv

## Affected
- Bitnami: `varnish` — affected >=7.1.0 <7.1.1

## Details
In Varnish Cache 7.0.0, 7.0.1, 7.0.2, and 7.1.0, it is possible to cause the Varnish Server to assert and automatically restart through forged HTTP/1 backend responses. An attack uses a crafted reason phrase of the backend response status line. This is fixed in 7.0.3 and 7.1.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M4KVVCIQVINQQ2D7ORNARSYALMJUMP3I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TW3X4PEKC5C736SCKE2UG3Y7JWKMD2K6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2BUKFICLZBXESLQ3MXMIG3G52RZURFK/
- https://varnish-cache.org/security/VSV00009.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-38150
