# [H] KVM: SVM: Serialize accesses to the owner and mirror list with separate lock

## Summary
Severity: High
Advisory: CVE-2026-74607
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74607
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: Serialize accesses to the owner and mirror list with separate lock

Interaction between KVM_CAP_VM_MOVE_ENC_CONTEXT_FROM and
KVM_CAP_VM_COPY_ENC_CONTEXT_FROM can cause two separate issues:

- in sev_migrate_from(), when the destination KVM is a mirror, the mirror
  entry is moved from the source's list to the owner's mirror_vms list,
  without holding the owner's lock unlike other writers of the owner's
  mirror list (sev_vm_copy_enc_context_from(), sev_vm_destroy()).
  A concurrent COPY or destroy can race with sev_migrate_from() and
  corrupt the list.

- In sev_vm_destroy(), the *owner* is still active and could receive
  concurrently a KVM_CAP_VM_MOVE_ENC_CONTEXT_FROM that causes
  sev->enc_context_owner to change.  In this case the incorrect VM
  receives kvm_put_kvm().

The second issue needs particular care because the owner could disappear
altogether (even though the race window is impossibly small) between
reading it and locking it.  There is thus no way to perform the checks
under the owner lock without putting struct kvm under SLAB_TYPESAFE_BY_RCU
(which would allow kvm_get_kvm_safe() under RCU critical section).

It is much simpler to just use a global lock, since the critical
sections are so small and the new lock is always a leaf lock.

## References
- https://git.kernel.org/stable/c/1d78d33275ef2a16c6d080910b291d0a97a0e613
- https://git.kernel.org/stable/c/28afde1edbd8b20058cbf4d75fb57876471ec334
- https://git.kernel.org/stable/c/328ab4fabe05af004d886659f8744076e320ddce
- https://git.kernel.org/stable/c/47976eaaf0a4eb46dade48b3246779090db9e3ec
- https://git.kernel.org/stable/c/7943ec3a6d0e7e0a2eb4943300bce089ac3e8c3e
- https://git.kernel.org/stable/c/d728baba0f20e49439fc7831bf3e4e7dee82161a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74607.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74607
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
