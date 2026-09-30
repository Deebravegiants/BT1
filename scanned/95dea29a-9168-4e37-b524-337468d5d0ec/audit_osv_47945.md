# [M] CVE-2017-15274

## Summary
Severity: Medium
Advisory: CVE-2017-15274
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-12
Source: https://osv.dev/vulnerability/CVE-2017-15274
Type: osv

## Details
security/keys/keyctl.c in the Linux kernel before 4.11.5 does not consider the case of a NULL payload in conjunction with a nonzero length value, which allows local users to cause a denial of service (NULL pointer dereference and OOPS) via a crafted add_key or keyctl system call, a different vulnerability than CVE-2017-12192.

## References
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- http://www.securityfocus.com/bid/101292
- https://access.redhat.com/errata/RHSA-2019:1946
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.5
- https://bugzilla.suse.com/show_bug.cgi?id=1045327
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5649645d725c73df4302428ee4e02c869248b4c5
- https://github.com/torvalds/linux/commit/5649645d725c73df4302428ee4e02c869248b4c5
- https://patchwork.kernel.org/patch/9781573/
