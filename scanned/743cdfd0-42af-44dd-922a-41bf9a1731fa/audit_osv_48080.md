# [H] CVE-2017-17856

## Summary
Severity: High
Advisory: CVE-2017-17856
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17856
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 4.14.8 allows local users to cause a denial of service (memory corruption) or possibly have unspecified other impact by leveraging the lack of stack-pointer alignment enforcement.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a5ec6ae161d72f01411169a938fa5f8baea16e8f
- http://www.openwall.com/lists/oss-security/2017/12/21/2
- https://github.com/torvalds/linux/commit/a5ec6ae161d72f01411169a938fa5f8baea16e8f
