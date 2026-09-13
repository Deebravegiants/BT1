# [M] CVE-2010-4020

## Summary
Severity: Medium
Advisory: CVE-2010-4020
CVSS: 6.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2010-12-02
Source: https://osv.dev/vulnerability/CVE-2010-4020
Type: osv

## Details
MIT Kerberos 5 (aka krb5) 1.8.x through 1.8.3 does not reject RC4 key-derivation checksums, which might allow remote authenticated users to forge a (1) AD-SIGNEDPATH or (2) AD-KDC-ISSUED signature, and possibly gain privileges, by leveraging the small key space that results from certain one-byte stream-cipher operations.

## References
- http://secunia.com/advisories/42399
- http://web.mit.edu/kerberos/advisories/MITKRB5-SA-2010-007.txt
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:246
- http://www.oracle.com/technetwork/topics/security/cpujul2015-2367936.html
- http://www.ubuntu.com/usn/USN-1030-1
- http://www.vmware.com/security/advisories/VMSA-2011-0007.html
- http://www.vupen.com/english/advisories/2010/3094
- http://www.vupen.com/english/advisories/2010/3095
- http://www.vupen.com/english/advisories/2010/3118
- http://www.oracle.com/technetwork/topics/security/cpujul2015-2367936.html
- http://kb.vmware.com/kb/1035108
- http://lists.apple.com/archives/security-announce/2011/Mar/msg00006.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-December/051976.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-December/051999.html
- http://lists.opensuse.org/opensuse-security-announce/2010-12/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2010-12/msg00006.html
- http://lists.vmware.com/pipermail/security-announce/2011/000133.html
- http://osvdb.org/69608
- http://support.apple.com/kb/HT4581
- http://www.redhat.com/support/errata/RHSA-2010-0925.html
