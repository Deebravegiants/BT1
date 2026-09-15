# [M] CVE-2016-10154

## Summary
Severity: Medium
Advisory: CVE-2016-10154
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-10154
Type: osv

## Details
The smbhash function in fs/cifs/smbencrypt.c in the Linux kernel 4.9.x before 4.9.1 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.1
- http://www.securityfocus.com/bid/95714
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=06deeec77a5a689cc94b21a8a91a76e42176685d
- http://www.openwall.com/lists/oss-security/2017/01/21/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1416104
- https://github.com/torvalds/linux/commit/06deeec77a5a689cc94b21a8a91a76e42176685d
