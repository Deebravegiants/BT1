# [M] CVE-2021-3631

## Summary
Severity: Medium
Advisory: CVE-2021-3631
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3631
Type: osv

## Details
A flaw was found in libvirt while it generates SELinux MCS category pairs for VMs' dynamic labels. This flaw allows one exploited guest to access files labeled for another guest, resulting in the breaking out of sVirt confinement. The highest threat from this vulnerability is to confidentiality and integrity.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://access.redhat.com/errata/RHSA-2021:3631
- https://security.gentoo.org/glsa/202210-06
- https://security.netapp.com/advisory/ntap-20220331-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=1977726
- https://gitlab.com/libvirt/libvirt/-/commit/15073504dbb624d3f6c911e85557019d3620fdb2
- https://gitlab.com/libvirt/libvirt/-/issues/153
