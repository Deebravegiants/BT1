# [H] CVE-2019-11071

## Summary
Severity: High
Advisory: CVE-2019-11071
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-10
Source: https://osv.dev/vulnerability/CVE-2019-11071
Type: osv

## Details
SPIP 3.1 before 3.1.10 and 3.2 before 3.2.4 allows authenticated visitors to execute arbitrary code on the host server because var_memotri is mishandled.

## References
- https://usn.ubuntu.com/4536-1/
- https://www.debian.org/security/2019/dsa-4429
- https://github.com/spip/SPIP/compare/1e3872c...9861a47
- https://blog.spip.net/Mise-a-jour-CRITIQUE-de-securite-Sortie-de-SPIP-3-1-10-et-SPIP-3-2-4.html
- https://github.com/spip/SPIP/commit/3ef87c525bc0768c926646f999a54222b37b5d36
- https://github.com/spip/SPIP/commit/824d17f424bf77d17af89c18c3dc807a3199567e
