# [C] KVM: arm64: vgic: Handle race between interrupt affinity change and LPI disabling

## Summary
Severity: Critical
Advisory: CVE-2026-72288
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72288
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic: Handle race between interrupt affinity change and LPI disabling

Hyunwoo Kim reports some really bad races should the following
situation occur:

- LPI-I is pending in vcpu-B's AP list
- vcpu-A writes to vcpu-B's RD to disable its LPIs
- vcpu-C moves I from B to C

If the last two race nicely enough, vgic_prune_ap_list() can drop
the irq and AP list locks, reacquire them, and in the interval
the irq has been freed. UAF follows.

The fix is two-fold:

- Before dropping the irq and ap_list locks, take a reference on
  the irq

- Do not try to handle migration of the pending bit: there is no
  expectation that this state is retained, as per the architecture

With that, we're sure that the interrupt is still around, and we
safely remove it from the AP list as it has no target at this
stage (unless another interrupt fires, but that's another story).

## References
- https://git.kernel.org/stable/c/7258770e5814f15e8308ebda82ac9acf6964ba8e
- https://git.kernel.org/stable/c/b1a89d12d35a8256d2b170ced0b1c86851f3def2
- https://git.kernel.org/stable/c/d19dca8194ebed371e624331c6be2cb73b562caf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72288.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
