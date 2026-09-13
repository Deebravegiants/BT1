# [H] CVE-2017-17857

## Summary
Severity: High
Advisory: CVE-2017-17857
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17857
Type: osv

## Details
The check_stack_boundary function in kernel/bpf/verifier.c in the Linux kernel through 4.14.8 allows local users to cause a denial of service (memory corruption) or possibly have unspecified other impact by leveraging mishandling of invalid variable stack read operations.

## References
- http://www.openwall.com/lists/oss-security/2017/12/21/2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ea25f914dc164c8d56b36147ecc86bc65f83c469
- https://github.com/torvalds/linux/commit/ea25f914dc164c8d56b36147ecc86bc65f83c469
