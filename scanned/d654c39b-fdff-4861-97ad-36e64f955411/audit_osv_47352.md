# [C] CVE-2016-3154

## Summary
Severity: Critical
Advisory: CVE-2016-3154
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-08
Source: https://osv.dev/vulnerability/CVE-2016-3154
Type: osv

## Details
The encoder_contexte_ajax function in ecrire/inc/filtres.php in SPIP 2.x before 2.1.19, 3.0.x before 3.0.22, and 3.1.x before 3.1.1 allows remote attackers to conduct PHP object injection attacks and execute arbitrary PHP code via a crafted serialized object.

## References
- https://core.spip.net/projects/spip/repository/revisions/22903
- http://www.debian.org/security/2016/dsa-3518
- https://blog.spip.net/Mise-a-jour-CRITIQUE-de-securite-Sortie-de-SPIP-3-1-1-SPIP-3-0-22-et-SPIP-2-1.html?lang=fr
