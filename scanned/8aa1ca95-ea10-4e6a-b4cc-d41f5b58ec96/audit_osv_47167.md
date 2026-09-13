# [M] CVE-2016-0823

## Summary
Severity: Medium
Advisory: CVE-2016-0823
CVSS: 4.0 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-03-12
Source: https://osv.dev/vulnerability/CVE-2016-0823
Type: osv

## Details
The pagemap_open function in fs/proc/task_mmu.c in the Linux kernel before 3.19.3, as used in Android 6.0.1 before 2016-03-01, allows local users to obtain sensitive physical-address information by reading a pagemap file, aka Android internal bug 25739721.

## References
- http://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.19.3
- http://www.securityfocus.com/bid/84265
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ab676b7d6fbf4b294bf198fb27ade5b0e865c7ce
- http://source.android.com/security/bulletin/2016-03-01.html
- https://github.com/torvalds/linux/commit/ab676b7d6fbf4b294bf198fb27ade5b0e865c7ce
- http://googleprojectzero.blogspot.com/2015/03/exploiting-dram-rowhammer-bug-to-gain.html
