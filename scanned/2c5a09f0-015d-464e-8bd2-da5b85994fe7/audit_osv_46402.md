# [M] CVE-2009-2408

## Summary
Severity: Medium
Advisory: CVE-2009-2408
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2009-07-30
Source: https://osv.dev/vulnerability/CVE-2009-2408
Type: osv

## Details
Mozilla Network Security Services (NSS) before 3.12.3, Firefox before 3.0.13, Thunderbird before 2.0.0.23, and SeaMonkey before 1.1.18 do not properly handle a '\0' character in a domain name in the subject's Common Name (CN) field of an X.509 certificate, which allows man-in-the-middle attackers to spoof arbitrary SSL servers via a crafted certificate issued by a legitimate Certification Authority. NOTE: this was originally reported for Firefox before 3.5.

## References
- http://secunia.com/advisories/36088
- http://secunia.com/advisories/36125
- http://secunia.com/advisories/36139
- http://secunia.com/advisories/36157
- http://secunia.com/advisories/36434
- http://secunia.com/advisories/36669
- http://secunia.com/advisories/37098
- http://www.mandriva.com/security/advisories?name=MDVSA-2009:197
- http://www.mandriva.com/security/advisories?name=MDVSA-2009:216
- http://www.mandriva.com/security/advisories?name=MDVSA-2009:217
- http://www.mozilla.org/security/announce/2009/mfsa2009-42.html
- http://www.novell.com/linux/security/advisories/2009_48_firefox.html
- http://www.securitytracker.com/id?1022632
- http://www.ubuntu.com/usn/usn-810-1
- http://www.vupen.com/english/advisories/2009/2085
- http://www.vupen.com/english/advisories/2009/3184
- http://lists.opensuse.org/opensuse-security-announce/2009-11/msg00004.html
- http://marc.info/?l=oss-security&m=125198917018936&w=2
- http://www.debian.org/security/2009/dsa-1874
- https://bugzilla.redhat.com/show_bug.cgi?id=510251
