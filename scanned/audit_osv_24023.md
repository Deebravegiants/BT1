# [H] KVM: Initialize gfn_to_pfn_cache locks in dedicated helper

## Summary
Severity: High
Advisory: CVE-2022-49884
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49884
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Initialize gfn_to_pfn_cache locks in dedicated helper

Move the gfn_to_pfn_cache lock initialization to another helper and
call the new helper during VM/vCPU creation.  There are race
conditions possible due to kvm_gfn_to_pfn_cache_init()'s
ability to re-initialize the cache's locks.

For example: a race between ioctl(KVM_XEN_HVM_EVTCHN_SEND) and
kvm_gfn_to_pfn_cache_init() leads to a corrupted shinfo gpc lock.

                (thread 1)                |           (thread 2)
                                          |
 kvm_xen_set_evtchn_fast                  |
  read_lock_irqsave(&gpc->lock, ...)      |
                                          | kvm_gfn_to_pfn_cache_init
                                          |  rwlock_init(&gpc->lock)
  read_unlock_irqrestore(&gpc->lock, ...) |

Rename "cache_init" and "cache_destroy" to activate+deactivate to
avoid implying that the cache really is destroyed/freed.

Note, there more races in the newly named kvm_gpc_activate() that will
be addressed separately.

[sean: call out that this is a bug fix]

## References
- https://git.kernel.org/stable/c/52491a38b2c2411f3f0229dc6ad610349c704a41
- https://git.kernel.org/stable/c/61242001d6c9c253df7645dab090842d8da08764
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49884.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49884
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
