# [M] CVE-2014-3647

## Summary
Severity: Medium
Advisory: CVE-2014-3647
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-3647
Type: osv

## Details
arch/x86/kvm/emulate.c in the KVM subsystem in the Linux kernel through 3.17.2 does not properly perform RIP changes, which allows guest OS users to cause a denial of service (guest OS crash) via a crafted application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://www.debian.org/security/2014/dsa-3060
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securityfocus.com/bid/70748
- http://www.ubuntu.com/usn/USN-2394-1
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1144897
- https://github.com/torvalds/linux/commit/234f3ce485d54017f15cf5e0699cff4100121601
- https://github.com/torvalds/linux/commit/d1442d85cc30ea75f7d399474ca738e0bc96f715
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1144897
- https://github.com/torvalds/linux/commit/234f3ce485d54017f15cf5e0699cff4100121601
- https://github.com/torvalds/linux/commit/d1442d85cc30ea75f7d399474ca738e0bc96f715
- https://bugzilla.redhat.com/show_bug.cgi?id=1144897
