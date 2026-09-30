# [C] CVE-2010-0211

## Summary
Severity: Critical
Advisory: CVE-2010-0211
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2010-07-28
Source: https://osv.dev/vulnerability/CVE-2010-0211
Type: osv

## Details
The slap_modrdn2mods function in modrdn.c in OpenLDAP 2.4.22 does not check the return value of a call to the smr_normalize function, which allows remote attackers to cause a denial of service (segmentation fault) and possibly execute arbitrary code via a modrdn call with an RDN string containing invalid UTF-8 sequences, which triggers a free of an invalid, uninitialized pointer in the slap_mods_free function, as demonstrated using the Codenomicon LDAPv3 test suite.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10705
- http://secunia.com/advisories/40639
- http://secunia.com/advisories/40677
- http://secunia.com/advisories/40687
- http://secunia.com/advisories/42787
- http://security.gentoo.org/glsa/glsa-201406-36.xml
- http://www.securityfocus.com/archive/1/515545/100/0/threaded
- http://www.securityfocus.com/bid/41770
- http://www.securitytracker.com/id?1024221
- http://www.vmware.com/security/advisories/VMSA-2011-0001.html
- http://www.vupen.com/english/advisories/2010/1849
- http://www.vupen.com/english/advisories/2010/1858
- http://www.vupen.com/english/advisories/2011/0025
- http://lists.apple.com/archives/security-announce/2010//Nov/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2010-08/msg00001.html
- http://www.openldap.org/its/index.cgi/Software%20Bugs?id=6570
- http://www.securityfocus.com/bid/41770
- http://www.securityfocus.com/bid/41770
- http://support.apple.com/kb/HT4435
- http://www.redhat.com/support/errata/RHSA-2010-0542.html
