# [H] LoongArch: KVM: Check irq validity in kvm_vcpu_ioctl_interrupt()

## Summary
Severity: High
Advisory: CVE-2026-72294
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72294
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Check irq validity in kvm_vcpu_ioctl_interrupt()

Function kvm_vcpu_ioctl_interrupt() can be called from userspace, here
add irq validility cheking in kvm_vcpu_ioctl_interrupt().

## References
- https://git.kernel.org/stable/c/09b318ab77b7a4fc9987fd98d1525fc55ddc2617
- https://git.kernel.org/stable/c/15469ba0284c7cc01c38493391e9e73b918833c4
- https://git.kernel.org/stable/c/d4574547e04a47ad498149576f65b84475ea6f4c
- https://git.kernel.org/stable/c/efe27b19a15c384cad7c80de399f3107ab070e6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72294.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
