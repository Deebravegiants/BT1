# [C] CVE-2008-0062

## Summary
Severity: Critical
Advisory: CVE-2008-0062
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2008-03-19
Source: https://osv.dev/vulnerability/CVE-2008-0062
Type: osv

## Details
KDC in MIT Kerberos 5 (krb5kdc) does not set a global variable for some krb4 message types, which allows remote attackers to cause a denial of service (crash) and possibly execute arbitrary code via crafted messages that trigger a NULL pointer dereference or double-free.

## References
- http://secunia.com/advisories/29420
- http://secunia.com/advisories/29423
- http://secunia.com/advisories/29424
- http://secunia.com/advisories/29428
- http://secunia.com/advisories/29435
- http://secunia.com/advisories/29438
- http://secunia.com/advisories/29450
- http://secunia.com/advisories/29451
- http://secunia.com/advisories/29457
- http://secunia.com/advisories/29462
- http://secunia.com/advisories/29464
- http://secunia.com/advisories/29516
- http://secunia.com/advisories/29663
- http://secunia.com/advisories/30535
- http://web.mit.edu/kerberos/advisories/MITKRB5-SA-2008-001.txt
- http://www.debian.org/security/2008/dsa-1524
- http://www.gentoo.org/security/en/glsa/glsa-200803-31.xml
- http://www.kb.cert.org/vuls/id/895609
- http://www.mandriva.com/security/advisories?name=MDVSA-2008:069
- http://www.mandriva.com/security/advisories?name=MDVSA-2008:070
