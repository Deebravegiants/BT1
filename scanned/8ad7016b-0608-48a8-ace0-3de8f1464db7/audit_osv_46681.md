# [H] CVE-2014-8369

## Summary
Severity: High
Advisory: CVE-2014-8369
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-8369
Type: osv

## Details
The kvm_iommu_map_pages function in virt/kvm/iommu.c in the Linux kernel through 3.17.2 miscalculates the number of pages during the handling of a mapping failure, which allows guest OS users to cause a denial of service (host OS page unpinning) or possibly have unspecified other impact by leveraging guest OS privileges.  NOTE: this vulnerability exists because of an incorrect fix for CVE-2014-3601.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://rhn.redhat.com/errata/RHSA-2015-0674.html
- http://secunia.com/advisories/62326
- http://secunia.com/advisories/62336
- http://www.debian.org/security/2014/dsa-3093
- http://www.openwall.com/lists/oss-security/2014/10/24/7
- http://www.securityfocus.com/bid/70747
- http://www.securityfocus.com/bid/70749
- https://bugzilla.redhat.com/show_bug.cgi?id=1156518
- https://github.com/torvalds/linux/commit/3d32e4dbe71374a6780eaf51d719d76f9a9bf22f
- https://lkml.org/lkml/2014/10/24/460
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://www.openwall.com/lists/oss-security/2014/10/24/7
- https://lkml.org/lkml/2014/10/24/460
- https://github.com/torvalds/linux/commit/3d32e4dbe71374a6780eaf51d719d76f9a9bf22f
- https://lkml.org/lkml/2014/10/24/460
