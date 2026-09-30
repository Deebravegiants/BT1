# [H] CVE-2017-8797

## Summary
Severity: High
Advisory: CVE-2017-8797
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-02
Source: https://osv.dev/vulnerability/CVE-2017-8797
Type: osv

## Details
The NFSv4 server in the Linux kernel before 4.11.3 does not properly validate the layout type when processing the NFSv4 pNFS GETDEVICEINFO or LAYOUTGET operand in a UDP packet from a remote attacker. This type value is uninitialized upon encountering certain error conditions. This value is used as an array index for dereferencing, which leads to an OOPS and eventually a DoS of knfsd and a soft-lockup of the whole system.

## References
- http://www.securityfocus.com/bid/99298
- http://www.securitytracker.com/id/1038790
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2437
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.3
- https://bugzilla.redhat.com/show_bug.cgi?id=1466329
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b550a32e60a4941994b437a8d662432a486235a5
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f961e3f2acae94b727380c0b74e2d3954d0edf79
- http://www.openwall.com/lists/oss-security/2017/06/27/5
- https://github.com/torvalds/linux/commit/b550a32e60a4941994b437a8d662432a486235a5
- https://github.com/torvalds/linux/commit/f961e3f2acae94b727380c0b74e2d3954d0edf79
