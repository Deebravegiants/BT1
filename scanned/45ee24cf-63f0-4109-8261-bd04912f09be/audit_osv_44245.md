# [H] KVM: arm64: nv: Inject SEA if kvm_translate_vncr() can't resolve PFN

## Summary
Severity: High
Advisory: CVE-2026-80665
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80665
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Inject SEA if kvm_translate_vncr() can't resolve PFN

kvm_handle_vncr_abort() assumes that s1_walk_result conveys an abort
when kvm_translate_vncr() returns -EFAULT. This is not always the case
as it's possible to encounter 'late' failures on the output of S1
translation, e.g. a GFN outside of the memslots.

Fix it by preparing an external abort before returning from
kvm_translate_vncr(). Get rid of the BUG_ON() in the fault injection
path while at it.

## References
- https://git.kernel.org/stable/c/4ead4def04659739c399bfcb063f8a906194c79f
- https://git.kernel.org/stable/c/53804b6839573c9c6fff5f4cf075d6746267345e
- https://git.kernel.org/stable/c/9f3e83345a56280efffe235c65593c7e544c0fcc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80665.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
