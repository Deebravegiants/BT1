# [M] CVE-2022-2785

## Summary
Severity: Medium
Advisory: CVE-2022-2785
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-2785
Type: osv

## Details
There exists an arbitrary memory read within the Linux Kernel BPF - Constants provided to fill pointers in structs passed in to bpf_sys_bpf are not verified and can point anywhere, including memory not owned by BPF. An attacker with CAP_BPF can arbitrarily read memory from anywhere on the system. We recommend upgrading past commit 86f44fcec22c

## References
- https://lore.kernel.org/bpf/20220816205517.682470-1-zhuyifei%40google.com/T/#t
- https://git.kernel.org/bpf/bpf/c/86f44fcec22c
