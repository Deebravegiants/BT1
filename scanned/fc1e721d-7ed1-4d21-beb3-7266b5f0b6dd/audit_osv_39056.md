# [H] net/rds: reset op_nents when zerocopy page pin fails

## Summary
Severity: High
Advisory: CVE-2026-43494
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43494
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/rds: reset op_nents when zerocopy page pin fails

When iov_iter_get_pages2() fails in rds_message_zcopy_from_user(),
the pinned pages are released with put_page(), and
rm->data.op_mmp_znotifier is cleared.  But we fail to properly
clear rm->data.op_nents.

Later when rds_message_purge() is called from rds_sendmsg() the
cleanup loop iterates over the incorrectly non zero number of
op_nents and frees them again.

Fix this by properly resetting op_nents when it should be in
rds_message_zcopy_from_user().

## References
- http://www.openwall.com/lists/oss-security/2026/05/21/2
- https://git.kernel.org/stable/c/03014551938a0887fa55f18ce49b70158a9c0113
- https://git.kernel.org/stable/c/0bbbff00a15b1df2cac9014d6cf4b6890f473353
- https://git.kernel.org/stable/c/290e833d1acb1093bc121fcdc97f5e6161157479
- https://git.kernel.org/stable/c/640e37f58f991546a87540d067279c2c1fa9fe51
- https://git.kernel.org/stable/c/9115669faedccdda100428e2d26fd0aac8c50799
- https://git.kernel.org/stable/c/c6e51512a784c4a7b86e1a044988696e3b3721fa
- https://git.kernel.org/stable/c/d84ce1786ce40fdd3dd98db47aec5527817e1ef6
- https://git.kernel.org/stable/c/e174929793195e0cd6a4adb0cad731b39f9019b4
- https://github.com/v12-security/pocs/tree/main/pintheft
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43494.json
- https://access.redhat.com/security/cve/CVE-2026-43494
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43494.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43494
- https://bugzilla.redhat.com/show_bug.cgi?id=2480434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
