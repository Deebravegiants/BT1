# [H] KVM: x86/xen: Initialize Xen timer only once

## Summary
Severity: High
Advisory: CVE-2022-50227
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50227
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86/xen: Initialize Xen timer only once

Add a check for existing xen timers before initializing a new one.

Currently kvm_xen_init_timer() is called on every
KVM_XEN_VCPU_ATTR_TYPE_TIMER, which is causing the following ODEBUG
crash when vcpu->arch.xen.timer is already set.

ODEBUG: init active (active state 0)
object type: hrtimer hint: xen_timer_callbac0
RIP: 0010:debug_print_object+0x16e/0x250 lib/debugobjects.c:502
Call Trace:
__debug_object_init
debug_hrtimer_init
debug_init
hrtimer_init
kvm_xen_init_timer
kvm_xen_vcpu_set_attr
kvm_arch_vcpu_ioctl
kvm_vcpu_ioctl
vfs_ioctl

## References
- https://git.kernel.org/stable/c/9a9b5771e930f408c3419799000f76a9abaf2278
- https://git.kernel.org/stable/c/af735db31285fa699384c649be72a9f32ecbb665
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50227.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
