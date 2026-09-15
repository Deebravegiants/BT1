# [M] CVE-2022-3533

## Summary
Severity: Medium
Advisory: CVE-2022-3533
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3533
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been rated as problematic. This issue affects the function parse_usdt_arg of the file tools/lib/bpf/usdt.c of the component BPF. The manipulation of the argument reg_name leads to memory leak. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-211031.

## References
- https://vuldb.com/?id.211031
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=0dc9254e03704c75f2ebc9cbef2ce4de83fba603
