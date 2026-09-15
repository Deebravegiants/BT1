# [C] CVE-2005-0102

## Summary
Severity: Critical
Advisory: CVE-2005-0102
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2005-01-24
Source: https://osv.dev/vulnerability/CVE-2005-0102
Type: osv

## Details
Integer overflow in camel-lock-helper in Evolution 2.0.2 and earlier allows local users or remote malicious POP3 servers to execute arbitrary code via a length value of -1, which leads to a zero byte memory allocation and a buffer overflow.

## References
- http://distro.conectiva.com.br/atualizacoes/?id=a&anuncio=000925
- http://secunia.com/advisories/13830
- http://security.gentoo.org/glsa/glsa-200501-35.xml
- http://securitytracker.com/id?1012981
- http://www.debian.org/security/2005/dsa-673
- http://www.mandriva.com/security/advisories?name=MDKSA-2005:024
- http://www.redhat.com/support/errata/RHSA-2005-397.html
- http://www.securityfocus.com/bid/12354
- https://exchange.xforce.ibmcloud.com/vulnerabilities/19031
- http://www.debian.org/security/2005/dsa-673
- http://distro.conectiva.com.br/atualizacoes/?id=a&anuncio=000925
- http://www.debian.org/security/2005/dsa-673
- http://www.redhat.com/support/errata/RHSA-2005-397.html
- http://www.securityfocus.com/bid/12354
- http://distro.conectiva.com.br/atualizacoes/?id=a&anuncio=000925
- http://securitytracker.com/id?1012981
- http://www.redhat.com/support/errata/RHSA-2005-238.html
- http://www.redhat.com/support/errata/RHSA-2005-397.html
- http://www.securityfocus.com/bid/12354
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A9616
