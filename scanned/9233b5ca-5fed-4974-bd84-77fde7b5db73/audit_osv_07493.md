# [H] BIT-sqlite-2020-13871

## Summary
Severity: High
Advisory: BIT-sqlite-2020-13871
Aliases: A-192606047, ASB-A-192606047, CVE-2020-13871
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2020-13871
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.32.2 <3.32.3

## Details
SQLite 3.32.2 has a use-after-free in resetAccumulator in select.c because the parse tree rewrite for window functions is too late.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://lists.debian.org/debian-lts-announce/2020/08/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BN32AGQPMHZRNM6P6L5GZPETOWTGXOKP/
- https://security.gentoo.org/glsa/202007-26
- https://security.netapp.com/advisory/ntap-20200619-0002/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.sqlite.org/src/info/79eff1d0383179c4
- https://www.sqlite.org/src/info/c8d3b9f0a750a529
- https://www.sqlite.org/src/info/cd708fa84d2aaaea
- https://nvd.nist.gov/vuln/detail/CVE-2020-13871
