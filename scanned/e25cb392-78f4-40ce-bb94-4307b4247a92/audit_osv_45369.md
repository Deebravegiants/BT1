# [M] JLSEC-2026-1089

## Summary
Severity: Medium
Advisory: JLSEC-2026-1089
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1089
Type: osv

## Affected
- Julia: `Chafa_jll` — affected unspecified

## Details
chafa: NULL Pointer Dereference in function gif_internal_decode_frame at libnsgif.c:599 allows attackers to cause a denial of service (crash) via a crafted input file. in GitHub repository hpjansson/chafa prior to 1.10.2. chafa: NULL Pointer Dereference in function gif_internal_decode_frame at libnsgif.c:599 allows attackers to cause a denial of service (crash) via a crafted input file.

## References
- https://github.com/hpjansson/chafa/commit/e4b777c7b7c144cd16a0ea96108267b1004fe6c9
- https://github.com/hpjansson/chafa/commit/e4b777c7b7c144cd16a0ea96108267b1004fe6c9
- https://huntr.dev/bounties/104d8c5d-cac5-4baa-9ac9-291ea0bcab95
- https://huntr.dev/bounties/104d8c5d-cac5-4baa-9ac9-291ea0bcab95
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3PLHKTQYK6AO3M5NAVM3CDVQTZZS6MCO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3PLHKTQYK6AO3M5NAVM3CDVQTZZS6MCO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DIOAZPITFL2Y7Y6KHCZ4OIK7P7KWFN22/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DIOAZPITFL2Y7Y6KHCZ4OIK7P7KWFN22/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L54UEP5S254VP5FZWGFPHLTPMFJVOGYT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L54UEP5S254VP5FZWGFPHLTPMFJVOGYT/
