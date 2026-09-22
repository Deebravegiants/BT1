# [M] CVE-2019-18660

## Summary
Severity: Medium
Advisory: CVE-2019-18660
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-18660
Type: osv

## Details
The Linux kernel before 5.4.1 on powerpc allows Information Exposure because the Spectre-RSB mitigation is not in place for all applicable CPUs, aka CID-39e72bf96f58. This is related to arch/powerpc/kernel/entry_64.S and arch/powerpc/kernel/security.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYIFGYEDQXP5DVJQQUARQRK2PXKBKQGY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWWOOJKZ4NQYN4RMFIVJ3ZIXKJJI3MKP/
- https://usn.ubuntu.com/4228-1/
- https://usn.ubuntu.com/4228-2/
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4225-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.1
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4227-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://access.redhat.com/errata/RHSA-2020:0174
- https://seclists.org/bugtraq/2020/Jan/10
- https://usn.ubuntu.com/4227-2/
- http://www.openwall.com/lists/oss-security/2019/11/27/1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=39e72bf96f5847ba87cc5bd7a3ce0fed813dc9ad
- https://www.openwall.com/lists/oss-security/2019/11/27/1
