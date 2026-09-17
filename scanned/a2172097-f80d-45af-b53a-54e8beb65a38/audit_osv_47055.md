# [M] CVE-2015-8816

## Summary
Severity: Medium
Advisory: CVE-2015-8816
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2015-8816
Type: osv

## Details
The hub_activate function in drivers/usb/core/hub.c in the Linux kernel before 4.3.5 does not properly maintain a hub-interface data structure, which allows physically proximate attackers to cause a denial of service (invalid memory access and system crash) or possibly have unspecified other impact by unplugging a USB hub device.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e50293ef9775c5f1cf3fcc093037dd6a8c5684ea
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://source.android.com/security/bulletin/2016-07-01.html
- http://www.debian.org/security/2016/dsa-3503
