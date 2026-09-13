# [M] CVE-2019-19227

## Summary
Severity: Medium
Advisory: CVE-2019-19227
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/CVE-2019-19227
Type: osv

## Details
In the AppleTalk subsystem in the Linux kernel before 5.1, there is a potential NULL pointer dereference because register_snap_client may return NULL. This will lead to denial of service in net/appletalk/aarp.c and net/appletalk/ddp.c, as demonstrated by unregister_snap_client, aka CID-9804501fa122.

## References
- https://seclists.org/bugtraq/2020/Jan/10
- https://usn.ubuntu.com/4287-1/
- https://usn.ubuntu.com/4287-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4254-1/
- https://usn.ubuntu.com/4254-2/
- https://usn.ubuntu.com/4258-1/
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9804501fa1228048857910a6bf23e085aade37cc
