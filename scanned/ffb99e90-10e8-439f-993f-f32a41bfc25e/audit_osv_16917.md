# [M] CVE-2020-10711

## Summary
Severity: Medium
Advisory: CVE-2020-10711
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-22
Source: https://osv.dev/vulnerability/CVE-2020-10711
Type: osv

## Details
A NULL pointer dereference flaw was found in the Linux kernel's SELinux subsystem in versions before 5.7. This flaw occurs while importing the Commercial IP Security Option (CIPSO) protocol's category bitmap into the SELinux extensible bitmap via the' ebitmap_netlbl_import' routine. While processing the CIPSO restricted bitmap tag in the 'cipso_v4_parsetag_rbm' routine, it sets the security attribute to indicate that the category bitmap is present, even if it has not been allocated. This issue leads to a NULL pointer dereference issue while importing the same category bitmap into SELinux. This flaw allows a remote network user to crash the system kernel, resulting in a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4412-1/
- https://usn.ubuntu.com/4419-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://usn.ubuntu.com/4411-1/
- https://usn.ubuntu.com/4413-1/
- https://usn.ubuntu.com/4414-1/
- https://www.debian.org/security/2020/dsa-4698
- https://www.debian.org/security/2020/dsa-4699
- https://www.openwall.com/lists/oss-security/2020/05/12/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10711
