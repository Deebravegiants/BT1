# [M] net: microchip: vcap api: Fix possible memory leak for vcap_dup_rule()

## Summary
Severity: Medium
Advisory: CVE-2023-53303
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53303
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: microchip: vcap api: Fix possible memory leak for vcap_dup_rule()

Inject fault When select CONFIG_VCAP_KUNIT_TEST, the below memory leak
occurs. If kzalloc() for duprule succeeds, but the following
kmemdup() fails, the duprule, ckf and caf memory will be leaked. So kfree
them in the error path.

unreferenced object 0xffff122744c50600 (size 192):
  comm "kunit_try_catch", pid 346, jiffies 4294896122 (age 911.812s)
  hex dump (first 32 bytes):
    10 27 00 00 04 00 00 00 1e 00 00 00 2c 01 00 00  .'..........,...
    00 00 00 00 00 00 00 00 18 06 c5 44 27 12 ff ff  ...........D'...
  backtrace:
    [<00000000394b0db8>] __kmem_cache_alloc_node+0x274/0x2f8
    [<0000000001bedc67>] kmalloc_trace+0x38/0x88
    [<00000000b0612f98>] vcap_dup_rule+0x50/0x460
    [<000000005d2d3aca>] vcap_add_rule+0x8cc/0x1038
    [<00000000eef9d0f8>] test_vcap_xn_rule_creator.constprop.0.isra.0+0x238/0x494
    [<00000000cbda607b>] vcap_api_rule_remove_in_front_test+0x1ac/0x698
    [<00000000c8766299>] kunit_try_run_case+0xe0/0x20c
    [<00000000c4fe9186>] kunit_generic_run_threadfn_adapter+0x50/0x94
    [<00000000f6864acf>] kthread+0x2e8/0x374
    [<0000000022e639b3>] ret_from_fork+0x10/0x20

## References
- https://git.kernel.org/stable/c/281f65d29d6da1a9b6907fb0b145aaf34f4e4822
- https://git.kernel.org/stable/c/a26ba60413b2c8f95daf0ee0152cf82abd7bfbe4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53303.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
