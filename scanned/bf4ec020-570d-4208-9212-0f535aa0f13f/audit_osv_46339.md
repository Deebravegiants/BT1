# [C] CVE-2002-1347

## Summary
Severity: Critical
Advisory: CVE-2002-1347
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2002-12-18
Source: https://osv.dev/vulnerability/CVE-2002-1347
Type: osv

## Details
Multiple buffer overflows in Cyrus SASL library 2.1.9 and earlier allow remote attackers to cause a denial of service and possibly execute arbitrary code via (1) long inputs during user name canonicalization, (2) characters that need to be escaped during LDAP authentication using saslauthd, or (3) an off-by-one error in the log writer, which does not allocate space for the null character that terminates a string.

## References
- http://www.debian.org/security/2002/dsa-215
- http://www.securityfocus.com/advisories/4826
- http://www.securityfocus.com/bid/6347
- http://www.securityfocus.com/bid/6348
- http://www.securityfocus.com/bid/6349
- https://exchange.xforce.ibmcloud.com/vulnerabilities/10810
- https://exchange.xforce.ibmcloud.com/vulnerabilities/10811
- https://exchange.xforce.ibmcloud.com/vulnerabilities/10812
- http://lists.apple.com/archives/security-announce/2005/Mar/msg00000.html
- http://marc.info/?l=bugtraq&m=103946297703402&w=2
- http://marc.info/?l=bugtraq&m=103946297703402&w=2
- http://archives.neohapsis.com/archives/linux/suse/2002-q4/1275.html
- http://distro.conectiva.com/atualizacoes/?id=a&anuncio=000557
- http://www.redhat.com/support/errata/RHSA-2002-283.html
- http://www.securityfocus.com/bid/6347
- http://www.securityfocus.com/bid/6348
- http://www.securityfocus.com/bid/6349
