# [M] CVE-2020-25637

## Summary
Severity: Medium
Advisory: CVE-2020-25637
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-25637
Type: osv

## Details
A double free memory issue was found to occur in the libvirt API, in versions before 6.8.0, responsible for requesting information about network interfaces of a running QEMU domain. This flaw affects the polkit access control driver. Specifically, clients connecting to the read-write socket with limited ACL permissions could use this flaw to crash the libvirt daemon, resulting in a denial of service, or potentially escalate their privileges on the system. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00073.html
- https://security.gentoo.org/glsa/202210-06
- https://bugzilla.redhat.com/show_bug.cgi?id=1881037
