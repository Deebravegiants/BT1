# [H] CVE-2009-0115

## Summary
Severity: High
Advisory: CVE-2009-0115
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2009-03-30
Source: https://osv.dev/vulnerability/CVE-2009-0115
Type: osv

## Details
The Device Mapper multipathing driver (aka multipath-tools or device-mapper-multipath) 0.4.8, as used in SUSE openSUSE, SUSE Linux Enterprise Server (SLES), Fedora, and possibly other operating systems, uses world-writable permissions for the socket file (aka /var/run/multipathd.sock), which allows local users to send arbitrary commands to the multipath daemon.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10691
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10705
- http://launchpad.net/bugs/cve/2009-0115
- http://secunia.com/advisories/34418
- http://secunia.com/advisories/34642
- http://secunia.com/advisories/34694
- http://secunia.com/advisories/34710
- http://secunia.com/advisories/34759
- http://secunia.com/advisories/38794
- http://support.avaya.com/elmodocs2/security/ASA-2009-128.htm
- http://www.debian.org/security/2009/dsa-1767
- http://lists.opensuse.org/opensuse-security-announce/2009-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2009-04/msg00003.html
- https://www.redhat.com/archives/fedora-package-announce/2009-April/msg00231.html
- https://www.redhat.com/archives/fedora-package-announce/2009-April/msg00236.html
- http://download.opensuse.org/update/10.3-test/repodata/patch-kpartx-6082.xml
- http://www.vupen.com/english/advisories/2010/0528
- http://download.opensuse.org/update/10.3-test/repodata/patch-kpartx-6082.xml
- http://lists.vmware.com/pipermail/security-announce/2010/000082.html
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A9214
