# [M] CVE-2020-27777

## Summary
Severity: Medium
Advisory: CVE-2020-27777
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-27777
Type: osv

## Details
A flaw was found in the way RTAS handled memory accesses in userspace to kernel communication. On a locked down (usually due to Secure Boot) guest system running on top of PowerVM or KVM hypervisors (pseries platform) a root like local user could use this flaw to further increase their privileges to that of a running kernel.

## References
- https://www.openwall.com/lists/oss-security/2020/11/23/2
- https://www.openwall.com/lists/oss-security/2020/10/09/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1900844
- https://git.kernel.org/pub/scm/linux/kernel/git/powerpc/linux.git/commit/?h=next&id=bd59380c5ba4147dcbaad3e582b55ccfd120b764
