# [H] CVE-2006-4434

## Summary
Severity: High
Advisory: CVE-2006-4434
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2006-08-29
Source: https://osv.dev/vulnerability/CVE-2006-4434
Type: osv

## Details
Use-after-free vulnerability in Sendmail before 8.13.8 allows remote attackers to cause a denial of service (crash) via a long "header line", which causes a previously freed variable to be referenced. NOTE: the original developer has disputed the severity of this issue, saying "The only denial of service that is possible here is to fill up the disk with core dumps if the OS actually generates different core dumps (which is unlikely)... the bug is in the shutdown code (finis()) which leads directly to exit(3), i.e., the process would terminate anyway, no mail delivery or receiption is affected."

## References
- http://secunia.com/advisories/21637
- http://secunia.com/advisories/21641
- http://secunia.com/advisories/21696
- http://secunia.com/advisories/21700
- http://secunia.com/advisories/21749
- http://secunia.com/advisories/22369
- http://securitytracker.com/id?1016753
- http://www.debian.org/security/2006/dsa-1164
- http://www.mandriva.com/security/advisories?name=MDKSA-2006:156
- http://www.novell.com/linux/security/advisories/2006_21_sr.html
- http://www.openbsd.org/errata.html#sendmail3
- http://www.openbsd.org/errata38.html#sendmail3
- http://www.securityfocus.com/bid/19714
- http://www.sendmail.org/releases/8.13.8.html
- http://www.vupen.com/english/advisories/2006/3393
- http://www.vupen.com/english/advisories/2006/3994
- http://www.attrition.org/pipermail/vim/2006-August/000999.html
- http://secunia.com/advisories/21637
- http://secunia.com/advisories/21641
- http://securitytracker.com/id?1016753
