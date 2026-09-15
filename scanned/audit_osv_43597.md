# [H] drm/amdkfd: hold event_mutex while checkpointing CRIU events

## Summary
Severity: High
Advisory: CVE-2026-74446
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74446
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: hold event_mutex while checkpointing CRIU events

kfd_criu_checkpoint_events() counts the entries in p->event_idr via
kfd_get_num_events(), allocates an array sized to that count, and then
walks the same IDR to fill it. Neither the count nor the walk holds
p->event_mutex.

The CRIU checkpoint caller holds only p->mutex. Event create and destroy
(kfd_event_create()/kfd_event_destroy()) take p->event_mutex and do not
take p->mutex, so a second thread in the same process can insert or remove
events between the count and the walk. If an event is inserted, the walk
iterates more entries than were counted and writes past the end of the
ev_privs allocation; if an event is removed, the walk dereferences an
entry that is being freed.

Hold p->event_mutex across the count and the walk so both observe a
consistent view of p->event_idr. The lock is released before
copy_to_user(), which only touches the local buffer. The caller already
holds p->mutex and the create/destroy paths never take p->mutex, so the
p->mutex -> p->event_mutex order is not inverted and no deadlock is
introduced.

(cherry picked from commit ff57e223ab105795b05d3ef3f3c35a5a441bcbaa)

## References
- https://git.kernel.org/stable/c/2040b7e39027cb83bb8c7b84a4c95c2f6053c32f
- https://git.kernel.org/stable/c/6a52f48157fa7fb81e0c146937fd6c8b0c1cfdbd
- https://git.kernel.org/stable/c/8f7196f25b14f4290738639a50459b56a5ff2784
- https://git.kernel.org/stable/c/9a7f765985f64fd4a7a58f7bc9cd80a1f4230628
- https://git.kernel.org/stable/c/bed80be08c0bee47fa242a4256ac873477c815f8
- https://git.kernel.org/stable/c/ff8bc5a68a9a70bdc38d61a72c7a49c56063f9d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
