# [M] CVE-2016-7914

## Summary
Severity: Medium
Advisory: CVE-2016-7914
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7914
Type: osv

## Details
The assoc_array_insert_into_terminal_node function in lib/assoc_array.c in the Linux kernel before 4.5.3 does not check whether a slot is a leaf, which allows local users to obtain sensitive information from kernel memory or cause a denial of service (invalid pointer dereference and out-of-bounds read) via an application that uses associative-array data structures, as demonstrated by the keyutils test suite.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.3
- http://www.securityfocus.com/bid/94138
- https://github.com/torvalds/linux/commit/8d4a2ec1e0b41b0cf9a0c5cd4511da7f8e4f3de2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8d4a2ec1e0b41b0cf9a0c5cd4511da7f8e4f3de2
