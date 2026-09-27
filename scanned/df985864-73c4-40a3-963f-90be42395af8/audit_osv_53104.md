# [H] CVE-2022-28960

## Summary
Severity: High
Advisory: CVE-2022-28960
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-19
Source: https://osv.dev/vulnerability/CVE-2022-28960
Type: osv

## Details
A PHP injection vulnerability in Spip before v3.2.8 allows attackers to execute arbitrary PHP code via the _oups parameter at /ecrire.

## References
- https://www.root-me.org/fr/Informations/Faiblesses-decouvertes/
- https://blog.spip.net/Mise-a-jour-CRITIQUE-de-securite-SPIP-3-2-8-et-SPIP-3-1-13.html
- https://github.com/spip/SPIP/commit/0394b44774555ae8331b6e65e35065dfa0bb41e4
- https://github.com/spip/SPIP/commit/6c1650713fc948318852ace759aab8f1a84791cf
- https://thinkloveshare.com/en/hacking/rce_on_spip_and_root_me/
