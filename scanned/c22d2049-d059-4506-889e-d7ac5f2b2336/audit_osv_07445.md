# [M] BIT-roundcube-2021-26925

## Summary
Severity: Medium
Advisory: BIT-roundcube-2021-26925
Aliases: CVE-2021-26925
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-roundcube-2021-26925
Type: osv

## Affected
- Bitnami: `roundcube` — affected >=0 <1.4.11

## Details
Roundcube before 1.4.11 allows XSS via crafted Cascading Style Sheets (CSS) token sequences during HTML email rendering.

## References
- https://github.com/roundcube/roundcubemail/commit/9dc276d5f26042db02754fa1bac6fbd683c6d596
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5QPAMYM2DQODSCQIAVNFJR2ETG7WMJOD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q752JPOHTR6H72FK3EIPJZ5O24Z7RGLM/
- https://roundcube.net/news/2021/02/08/security-update-1.4.11
