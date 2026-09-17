# [H] CVE-2018-10853

## Summary
Severity: High
Advisory: CVE-2018-10853
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2018-10853
Type: osv

## Details
A flaw was found in the way Linux kernel KVM hypervisor before 4.18 emulated instructions such as sgdt/sidt/fxsave/fxrstor. It did not check current privilege(CPL) level while emulating unprivileged instructions. An unprivileged guest user/process could use this flaw to potentially escalate privileges inside guest.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00043.html
- https://access.redhat.com/errata/RHSA-2020:0179
- https://access.redhat.com/errata/RHSA-2020:0103
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3777-1/
- https://access.redhat.com/errata/RHSA-2019:2043
- https://access.redhat.com/errata/RHSA-2020:0036
- https://usn.ubuntu.com/3777-2/
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://access.redhat.com/errata/RHSA-2019:2029
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10853
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=129a72a0d3c8e139a04512325384fe5ac119e74
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3c9fa24ca7c9c47605672916491f79e8ccacb9e6
- https://www.openwall.com/lists/oss-security/2018/09/02/1
