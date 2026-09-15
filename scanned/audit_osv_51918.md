# [M] CVE-2021-45402

## Summary
Severity: Medium
Advisory: CVE-2021-45402
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-11
Source: https://osv.dev/vulnerability/CVE-2021-45402
Type: osv

## Details
The check_alu_op() function in kernel/bpf/verifier.c in the Linux kernel through v5.16-rc5 did not properly update bounds while handling the mov32 instruction, which allows local users to obtain potentially sensitive address information, aka a "pointer leak."

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=3cf2b61eb06765e27fec6799292d9fb46d0b7e60
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=b1a7288dedc6caf9023f2676b4f5ed34cf0d4029
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=e572ff80f05c33cd0cb4860f864f5c9c044280b6
