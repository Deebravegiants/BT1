# [H] CVE-2010-2547

## Summary
Severity: High
Advisory: CVE-2010-2547
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2010-08-05
Source: https://osv.dev/vulnerability/CVE-2010-2547
Type: osv

## Details
Use-after-free vulnerability in kbx/keybox-blob.c in GPGSM in GnuPG 2.x through 2.0.16 allows remote attackers to cause a denial of service (crash) and possibly execute arbitrary code via a certificate with a large number of Subject Alternate Names, which is not properly handled in a realloc operation when importing the certificate or verifying its signature.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2010-August/044935.html
- http://lists.gnupg.org/pipermail/gnupg-announce/2010q3/000302.html
- http://lists.opensuse.org/opensuse-security-announce/2010-11/msg00001.html
- http://secunia.com/advisories/38877
- http://secunia.com/advisories/40718
- http://secunia.com/advisories/40841
- http://www.debian.org/security/2010/dsa-2076
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:143
- http://www.securityfocus.com/bid/41945
- http://www.securitytracker.com/id?1024247
- http://www.vupen.com/english/advisories/2010/1931
- http://www.vupen.com/english/advisories/2010/1950
- http://www.vupen.com/english/advisories/2010/1988
- http://www.vupen.com/english/advisories/2010/2217
- http://www.vupen.com/english/advisories/2010/3125
- http://lists.fedoraproject.org/pipermail/package-announce/2010-August/044935.html
- http://lists.opensuse.org/opensuse-security-announce/2010-11/msg00001.html
- http://www.debian.org/security/2010/dsa-2076
- http://lists.gnupg.org/pipermail/gnupg-announce/2010q3/000302.html
- http://slackware.com/security/viewer.php?l=slackware-security&y=2010&m=slackware-security.462008
