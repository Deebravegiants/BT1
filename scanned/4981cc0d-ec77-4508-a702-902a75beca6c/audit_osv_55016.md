# [C] CVE-2024-8517

## Summary
Severity: Critical
Advisory: CVE-2024-8517
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-06
Source: https://osv.dev/vulnerability/CVE-2024-8517
Type: osv

## Details
SPIP before 4.3.2, 4.2.16, and 
4.1.18 is vulnerable to a command injection issue. A 
remote and unauthenticated attacker can execute arbitrary operating system commands by sending a crafted multipart file upload HTTP request.

## References
- https://vulncheck.com/advisories/spip-upload-rce
- https://blog.spip.net/Mise-a-jour-critique-de-securite-sortie-de-SPIP-4-3-2-SPIP-4-2-16-SPIP-4-1-18.html
- https://thinkloveshare.com/hacking/spip_preauth_rce_2024_part_2_a_big_upload/
- https://vozec.fr/researchs/spip-preauth-rce-2024-big-upload/
