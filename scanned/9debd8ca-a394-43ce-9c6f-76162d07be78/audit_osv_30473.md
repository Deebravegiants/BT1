# [M] slub/kunit: fix a WARNING due to unwrapped __kmalloc_cache_noprof

## Summary
Severity: Medium
Advisory: CVE-2024-53049
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53049
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

slub/kunit: fix a WARNING due to unwrapped __kmalloc_cache_noprof

'modprobe slub_kunit' will have a warning as shown below. The root cause
is that __kmalloc_cache_noprof was directly used, which resulted in no
alloc_tag being allocated. This caused current->alloc_tag to be null,
leading to a warning in alloc_tag_add_check.

Let's add an alloc_hook layer to __kmalloc_cache_noprof specifically
within lib/slub_kunit.c, which is the only user of this internal slub
function outside kmalloc implementation itself.

[58162.947016] WARNING: CPU: 2 PID: 6210 at
./include/linux/alloc_tag.h:125 alloc_tagging_slab_alloc_hook+0x268/0x27c
[58162.957721] Call trace:
[58162.957919]  alloc_tagging_slab_alloc_hook+0x268/0x27c
[58162.958286]  __kmalloc_cache_noprof+0x14c/0x344
[58162.958615]  test_kmalloc_redzone_access+0x50/0x10c [slub_kunit]
[58162.959045]  kunit_try_run_case+0x74/0x184 [kunit]
[58162.959401]  kunit_generic_run_threadfn_adapter+0x2c/0x4c [kunit]
[58162.959841]  kthread+0x10c/0x118
[58162.960093]  ret_from_fork+0x10/0x20
[58162.960363] ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/2b059d0d1e624adc6e69a754bc48057f8bf459dc
- https://git.kernel.org/stable/c/79aea7dfd98fbbf282d1408fc21849fc9a677768
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53049.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53049
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
