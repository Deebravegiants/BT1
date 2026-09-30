# [M] CVE-2016-9178

## Summary
Severity: Medium
Advisory: CVE-2016-9178
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-9178
Type: osv

## Details
The __get_user_asm_ex macro in arch/x86/include/asm/uaccess.h in the Linux kernel before 4.7.5 does not initialize a certain integer variable, which allows local users to obtain sensitive information from kernel stack memory by triggering failure of a get_user_ex call.

## References
- http://www.securityfocus.com/bid/94144
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.5
- http://www.openwall.com/lists/oss-security/2016/11/04/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1391908
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1c109fabbd51863475cd12ac206bdd249aee35af
- https://github.com/torvalds/linux/commit/1c109fabbd51863475cd12ac206bdd249aee35af
