# [H] CVE-2019-11924

## Summary
Severity: High
Advisory: CVE-2019-11924
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-20
Source: https://osv.dev/vulnerability/CVE-2019-11924
Type: osv

## Details
A peer could send empty handshake fragments containing only padding which would be kept in memory until a full handshake was received, resulting in memory exhaustion. This issue affects versions v2019.01.28.00 and above of fizz, until v2019.08.05.00.

## References
- https://www.facebook.com/security/advisories/cve-2019-11924
- https://github.com/facebookincubator/fizz/commit/3eaddb33619eaaf74a760872850c550ad8f5c52f
- https://github.com/facebookincubator/fizz/commit/6bf67137ef1ee5cd70c842b014c322b7deaf994b
