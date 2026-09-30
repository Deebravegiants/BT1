# [M] CVE-2020-27673

## Summary
Severity: Medium
Advisory: CVE-2020-27673
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-22
Source: https://osv.dev/vulnerability/CVE-2020-27673
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.9.1, as used with Xen through 4.14.x. Guest OS users can cause a denial of service (host OS hang) via a high rate of events to dom0, aka CID-e99502f76271.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00025.html
- http://www.openwall.com/lists/oss-security/2021/01/19/6
- https://security.gentoo.org/glsa/202011-06
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00075.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e99502f76271d6bc4e374fe368c50c67a1fd3070
- https://xenbits.xen.org/xsa/advisory-332.html
- https://github.com/torvalds/linux/commit/e99502f76271d6bc4e374fe368c50c67a1fd3070
