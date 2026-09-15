# [H] bfq: Update cgroup information before merging bio

## Summary
Severity: High
Advisory: CVE-2022-49413
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49413
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bfq: Update cgroup information before merging bio

When the process is migrated to a different cgroup (or in case of
writeback just starts submitting bios associated with a different
cgroup) bfq_merge_bio() can operate with stale cgroup information in
bic. Thus the bio can be merged to a request from a different cgroup or
it can result in merging of bfqqs for different cgroups or bfqqs of
already dead cgroups and causing possible use-after-free issues. Fix the
problem by updating cgroup information in bfq_merge_bio().

## References
- https://git.kernel.org/stable/c/2a1077f17169a6059992a0bbdb330e0abad1e6d9
- https://git.kernel.org/stable/c/b06691af08b41dfd81052a3362514d9827b44bb1
- https://git.kernel.org/stable/c/d9165200c5627a2cf4408eefabdf0058bdf95e1a
- https://git.kernel.org/stable/c/da9f3025d595956410ceaab2bea01980d7775948
- https://git.kernel.org/stable/c/e8821f45612f2e6d9adb9c6ba0fb4184f57692aa
- https://git.kernel.org/stable/c/ea591cd4eb270393810e7be01feb8fde6a34fbbe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49413.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49413
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
