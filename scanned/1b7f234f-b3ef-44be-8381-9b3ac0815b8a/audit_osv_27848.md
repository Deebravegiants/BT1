# [H] fs/proc/task_mmu: move mmu notification mechanism inside mm lock

## Summary
Severity: High
Advisory: CVE-2024-26617
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-26617
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/proc/task_mmu: move mmu notification mechanism inside mm lock

Move mmu notification mechanism inside mm lock to prevent race condition
in other components which depend on it.  The notifier will invalidate
memory range.  Depending upon the number of iterations, different memory
ranges would be invalidated.

The following warning would be removed by this patch:
WARNING: CPU: 0 PID: 5067 at arch/x86/kvm/../../../virt/kvm/kvm_main.c:734 kvm_mmu_notifier_change_pte+0x860/0x960 arch/x86/kvm/../../../virt/kvm/kvm_main.c:734

There is no behavioural and performance change with this patch when
there is no component registered with the mmu notifier.

[akpm@linux-foundation.org: narrow the scope of `range', per Sean]

## References
- https://git.kernel.org/stable/c/05509adf297924f51e1493aa86f9fcde1433ed80
- https://git.kernel.org/stable/c/4cccb6221cae6d020270606b9e52b1678fc8b71a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26617.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26617
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
