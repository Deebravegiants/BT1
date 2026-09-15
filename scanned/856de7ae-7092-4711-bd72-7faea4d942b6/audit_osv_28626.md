# [H] KVM: SVM: Flush pages under kvm->lock to fix UAF in svm_register_enc_region()

## Summary
Severity: High
Advisory: CVE-2024-35791
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35791
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.215, >=5.11.0 <6.1.84, >=5.16.0 <6.6.24, >=6.2.0 <6.7.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: Flush pages under kvm->lock to fix UAF in svm_register_enc_region()

Do the cache flush of converted pages in svm_register_enc_region() before
dropping kvm->lock to fix use-after-free issues where region and/or its
array of pages could be freed by a different task, e.g. if userspace has
__unregister_enc_region_locked() already queued up for the region.

Note, the "obvious" alternative of using local variables doesn't fully
resolve the bug, as region->pages is also dynamically allocated.  I.e. the
region structure itself would be fine, but region->pages could be freed.

Flushing multiple pages under kvm->lock is unfortunate, but the entire
flow is a rare slow path, and the manual flush is only needed on CPUs that
lack coherency for encrypted memory.

## References
- https://git.kernel.org/stable/c/12f8e32a5a389a5d58afc67728c76e61beee1ad4
- https://git.kernel.org/stable/c/2d13b79640b147bd77c34a5998533b2021a4122d
- https://git.kernel.org/stable/c/4868c0ecdb6cfde7c70cf478c46e06bb9c7e5865
- https://git.kernel.org/stable/c/5ef1d8c1ddbf696e47b226e11888eaf8d9e8e807
- https://git.kernel.org/stable/c/e126b508ed2e616d679d85fca2fbe77bb48bbdd7
- https://git.kernel.org/stable/c/f6d53d8a2617dd58c89171a6b9610c470ebda38a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35791.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35791
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
