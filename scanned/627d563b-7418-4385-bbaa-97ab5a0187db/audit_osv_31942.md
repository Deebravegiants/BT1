# [H] KVM: arm64: Unconditionally save+flush host FPSIMD/SVE/SME state

## Summary
Severity: High
Advisory: CVE-2025-22013
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-22013
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Unconditionally save+flush host FPSIMD/SVE/SME state

There are several problems with the way hyp code lazily saves the host's
FPSIMD/SVE state, including:

* Host SVE being discarded unexpectedly due to inconsistent
  configuration of TIF_SVE and CPACR_ELx.ZEN. This has been seen to
  result in QEMU crashes where SVE is used by memmove(), as reported by
  Eric Auger:

  https://issues.redhat.com/browse/RHEL-68997

* Host SVE state is discarded *after* modification by ptrace, which was an
  unintentional ptrace ABI change introduced with lazy discarding of SVE state.

* The host FPMR value can be discarded when running a non-protected VM,
  where FPMR support is not exposed to a VM, and that VM uses
  FPSIMD/SVE. In these cases the hyp code does not save the host's FPMR
  before unbinding the host's FPSIMD/SVE/SME state, leaving a stale
  value in memory.

Avoid these by eagerly saving and "flushing" the host's FPSIMD/SVE/SME
state when loading a vCPU such that KVM does not need to save any of the
host's FPSIMD/SVE/SME state. For clarity, fpsimd_kvm_prepare() is
removed and the necessary call to fpsimd_save_and_flush_cpu_state() is
placed in kvm_arch_vcpu_load_fp(). As 'fpsimd_state' and 'fpmr_ptr'
should not be used, they are set to NULL; all uses of these will be
removed in subsequent patches.

Historical problems go back at least as far as v5.17, e.g. erroneous
assumptions about TIF_SVE being clear in commit:

  8383741ab2e773a9 ("KVM: arm64: Get rid of host SVE tracking/saving")

... and so this eager save+flush probably needs to be backported to ALL
stable trees.

## References
- https://git.kernel.org/stable/c/04c50cc23a492c4d43fdaefc7c1ecc0ff6f7b82e
- https://git.kernel.org/stable/c/5289ac43b69c61a49c75720921f2008005a31c43
- https://git.kernel.org/stable/c/79e140bba70bcacc5fe15bf8c0b958793fd7d56f
- https://git.kernel.org/stable/c/806d5c1e1d2e5502175a24bf70f251648d99c36a
- https://git.kernel.org/stable/c/900b444be493b7f404898c785d6605b177a093d0
- https://git.kernel.org/stable/c/fbc7e61195e23f744814e78524b73b59faa54ab4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22013.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22013
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
