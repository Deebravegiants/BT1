# [M] CVE-2023-1073

## Summary
Severity: Medium
Advisory: CVE-2023-1073
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1073
Type: osv

## Details
A memory corruption flaw was found in the Linux kernel’s human interface device (HID) subsystem in how a user inserts a malicious USB device. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://www.openwall.com/lists/osssecurity/2023/01/17/3
- http://www.openwall.com/lists/oss-security/2023/11/05/2
- http://www.openwall.com/lists/oss-security/2023/11/05/3
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2173403
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/id=b12fece4c64857e5fab4290bf01b2e0317a88456
