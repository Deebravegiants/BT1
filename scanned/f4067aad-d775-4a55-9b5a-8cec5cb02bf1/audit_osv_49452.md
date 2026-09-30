# [M] CVE-2019-12382

## Summary
Severity: Medium
Advisory: CVE-2019-12382
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2019-12382
Type: osv

## Details
An issue was discovered in drm_load_edid_firmware in drivers/gpu/drm/drm_edid_load.c in the Linux kernel through 5.1.5. There is an unchecked kstrdup of fwstr, which might allow an attacker to cause a denial of service (NULL pointer dereference and system crash). NOTE: The vendor disputes this issues as not being a vulnerability because kstrdup() returning NULL is handled sufficiently and there is no chance for a NULL pointer dereference

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J36BIJTKEPUOZKJNHQBUZA47RQONUKOI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KLGWJKLMTBBB53D5QLS4HOY2EH246WBE/
- https://lore.kernel.org/lkml/87o93u7d3s.fsf%40intel.com/
- https://salsa.debian.org/kernel-team/kernel-sec/blob/master/retired/CVE-2019-12382
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://www.securityfocus.com/bid/108474
- https://cgit.freedesktop.org/drm/drm-misc/commit/?id=9f1f1a2dab38d4ce87a13565cf4dc1b73bef3a5f
- https://lkml.org/lkml/2019/5/24/843
