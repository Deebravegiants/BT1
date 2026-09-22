# [H] CVE-2017-6874

## Summary
Severity: High
Advisory: CVE-2017-6874
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2017-6874
Type: osv

## Details
Race condition in kernel/ucount.c in the Linux kernel through 4.10.2 allows local users to cause a denial of service (use-after-free and system crash) or possibly have unspecified other impact via crafted system calls that leverage certain decrement behavior that causes incorrect interaction between put_ucounts and get_ucounts.

## References
- http://www.securityfocus.com/bid/96856
- https://github.com/torvalds/linux/commit/040757f738e13caaa9c5078bca79aa97e11dde88
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=040757f738e13caaa9c5078bca79aa97e11dde88
