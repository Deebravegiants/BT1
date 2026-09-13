# [H] KVM: Move kvm_io_bus_get_dev() locking responsibilities to callers

## Summary
Severity: High
Advisory: CVE-2026-72282
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72282
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Move kvm_io_bus_get_dev() locking responsibilities to callers

kvm_io_bus_get_dev() returns a device that is only matched by the
address, and nothing else. This can cause a lifetime issue if
the matched device is not the expected type, as by the time
the caller can introspect the object, it might be gone (the srcu
lock having been dropped).

Given that there is only a single user of this helper, the simplest
option is to move the locking responsibility to the caller, which
can keep the srcu lock held for as long as it wants.

Note that this aligns with other kvm_io_bus*() helpers, which
already require the srcu lock to be held by the callers.

## References
- https://git.kernel.org/stable/c/0cbae0e296d27ce4c4cce83e34d40c2bfd8133aa
- https://git.kernel.org/stable/c/1b4a3c2f0509e7b0e65667f3c36676a849ee2755
- https://git.kernel.org/stable/c/3a07249981629ace483ebbef81ef6b34c2d2afec
- https://git.kernel.org/stable/c/7099e7148f81c605bbc319b16ce0131540341560
- https://git.kernel.org/stable/c/90d35d2b8e47afd68fe2a4dd0eeb60bc71641775
- https://git.kernel.org/stable/c/cfe107b02a3c3f049e0dc15b6a36625f048eda2a
- https://git.kernel.org/stable/c/e01071ea006c9b952125ed8b0cc90ac7bd356cce
- https://git.kernel.org/stable/c/f398b7d92cd999191249830b9171c9bd787a9a91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72282.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72282
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
