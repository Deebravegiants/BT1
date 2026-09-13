# [H] KVM: Reject attempts to consume or refresh inactive gfn_to_pfn_cache

## Summary
Severity: High
Advisory: CVE-2022-49882
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49882
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Reject attempts to consume or refresh inactive gfn_to_pfn_cache

Reject kvm_gpc_check() and kvm_gpc_refresh() if the cache is inactive.
Not checking the active flag during refresh is particularly egregious, as
KVM can end up with a valid, inactive cache, which can lead to a variety
of use-after-free bugs, e.g. consuming a NULL kernel pointer or missing
an mmu_notifier invalidation due to the cache not being on the list of
gfns to invalidate.

Note, "active" needs to be set if and only if the cache is on the list
of caches, i.e. is reachable via mmu_notifier events.  If a relevant
mmu_notifier event occurs while the cache is "active" but not on the
list, KVM will not acquire the cache's lock and so will not serailize
the mmu_notifier event with active users and/or kvm_gpc_refresh().

A race between KVM_XEN_ATTR_TYPE_SHARED_INFO and KVM_XEN_HVM_EVTCHN_SEND
can be exploited to trigger the bug.

1. Deactivate shinfo cache:

kvm_xen_hvm_set_attr
case KVM_XEN_ATTR_TYPE_SHARED_INFO
 kvm_gpc_deactivate
  kvm_gpc_unmap
   gpc->valid = false
   gpc->khva = NULL
  gpc->active = false

Result: active = false, valid = false

2. Cause cache refresh:

kvm_arch_vm_ioctl
case KVM_XEN_HVM_EVTCHN_SEND
 kvm_xen_hvm_evtchn_send
  kvm_xen_set_evtchn
   kvm_xen_set_evtchn_fast
    kvm_gpc_check
    return -EWOULDBLOCK because !gpc->valid
   kvm_xen_set_evtchn_fast
    return -EWOULDBLOCK
   kvm_gpc_refresh
    hva_to_pfn_retry
     gpc->valid = true
     gpc->khva = not NULL

Result: active = false, valid = true

3. Race ioctl KVM_XEN_HVM_EVTCHN_SEND against ioctl
KVM_XEN_ATTR_TYPE_SHARED_INFO:

kvm_arch_vm_ioctl
case KVM_XEN_HVM_EVTCHN_SEND
 kvm_xen_hvm_evtchn_send
  kvm_xen_set_evtchn
   kvm_xen_set_evtchn_fast
    read_lock gpc->lock
                                          kvm_xen_hvm_set_attr case
                                          KVM_XEN_ATTR_TYPE_SHARED_INFO
                                           mutex_lock kvm->lock
                                           kvm_xen_shared_info_init
                                            kvm_gpc_activate
                                             gpc->khva = NULL
    kvm_gpc_check
     [ Check passes because gpc->valid is
       still true, even though gpc->khva
       is already NULL. ]
    shinfo = gpc->khva
    pending_bits = shinfo->evtchn_pending
    CRASH: test_and_set_bit(..., pending_bits)

## References
- https://git.kernel.org/stable/c/bfa9672f8fc9eb118124bab61899d2dd497f95ba
- https://git.kernel.org/stable/c/ecbcf030b45666ad11bc98565e71dfbcb7be4393
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49882.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49882
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
