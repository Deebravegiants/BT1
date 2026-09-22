# [H] CVE-2002-1372

## Summary
Severity: High
Advisory: CVE-2002-1372
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2002-12-26
Source: https://osv.dev/vulnerability/CVE-2002-1372
Type: osv

## Details
Common Unix Printing System (CUPS) 1.1.14 through 1.1.17 does not properly check the return values of various file and socket operations, which could allow a remote attacker to cause a denial of service (resource exhaustion) by causing file descriptors to be assigned and not released, as demonstrated by fanta.

## References
- http://www.debian.org/security/2003/dsa-232
- http://www.idefense.com/advisory/12.19.02.txt
- http://www.mandrakesoft.com/security/advisories?name=MDKSA-2003:001
- http://www.novell.com/linux/security/advisories/2003_002_cups.html
- http://www.securityfocus.com/bid/6440
- https://exchange.xforce.ibmcloud.com/vulnerabilities/10912
- http://marc.info/?l=bugtraq&m=104032149026670&w=2
- http://www.idefense.com/advisory/12.19.02.txt
- http://archives.neohapsis.com/archives/vulnwatch/2002-q4/0117.html
- http://distro.conectiva.com.br/atualizacoes/?id=a&anuncio=000702
- http://www.redhat.com/support/errata/RHSA-2002-295.html
- http://www.securityfocus.com/bid/6440
