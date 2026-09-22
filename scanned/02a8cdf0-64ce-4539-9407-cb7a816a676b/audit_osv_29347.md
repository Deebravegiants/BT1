# [H] bpf: Take return from set_memory_rox() into account with bpf_jit_binary_lock_ro()

## Summary
Severity: High
Advisory: CVE-2024-42067
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42067
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Take return from set_memory_rox() into account with bpf_jit_binary_lock_ro()

set_memory_rox() can fail, leaving memory unprotected.

Check return and bail out when bpf_jit_binary_lock_ro() returns
an error.

## References
- https://git.kernel.org/stable/c/044da7ae7afd4ef60806d73654a2e6a79aa4ed7a
- https://git.kernel.org/stable/c/08f6c05feb1db21653e98ca84ea04ca032d014c7
- https://git.kernel.org/stable/c/9fef36cad60d4226f9d06953cd56d1d2f9119730
- https://git.kernel.org/stable/c/e60adf513275c3a38e5cb67f7fd12387e43a3ff5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42067.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42067
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
