# [M] CVE-2017-9150

## Summary
Severity: Medium
Advisory: CVE-2017-9150
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-9150
Type: osv

## Details
The do_check function in kernel/bpf/verifier.c in the Linux kernel before 4.11.1 does not make the allow_ptr_leaks value available for restricting the output of the print_bpf_insn function, which allows local users to obtain sensitive address information via crafted bpf system calls.

## References
- https://www.exploit-db.com/exploits/42048/
- http://www.securityfocus.com/bid/98635
- https://source.android.com/security/bulletin/2017-09-01
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0d0e57697f162da4aa218b5feafe614fb666db07
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1251
- https://github.com/torvalds/linux/commit/0d0e57697f162da4aa218b5feafe614fb666db07
