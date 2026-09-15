# [M] coresight: Fix memory leak in acpi_buffer->pointer

## Summary
Severity: Medium
Advisory: CVE-2023-53261
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53261
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

coresight: Fix memory leak in acpi_buffer->pointer

There are memory leaks reported by kmemleak:
...
unreferenced object 0xffff00213c141000 (size 1024):
  comm "systemd-udevd", pid 2123, jiffies 4294909467 (age 6062.160s)
  hex dump (first 32 bytes):
    04 00 00 00 02 00 00 00 18 10 14 3c 21 00 ff ff  ...........<!...
    00 00 00 00 00 00 00 00 03 00 00 00 10 00 00 00  ................
  backtrace:
    [<000000004b7c9001>] __kmem_cache_alloc_node+0x2f8/0x348
    [<00000000b0fc7ceb>] __kmalloc+0x58/0x108
    [<0000000064ff4695>] acpi_os_allocate+0x2c/0x68
    [<000000007d57d116>] acpi_ut_initialize_buffer+0x54/0xe0
    [<0000000024583908>] acpi_evaluate_object+0x388/0x438
    [<0000000017b2e72b>] acpi_evaluate_object_typed+0xe8/0x240
    [<000000005df0eac2>] coresight_get_platform_data+0x1b4/0x988 [coresight]
...

The ACPI buffer memory (buf.pointer) should be freed. But the buffer
is also used after returning from acpi_get_dsd_graph().
Move the temporary variables buf to acpi_coresight_parse_graph(),
and free it before the function return to prevent memory leak.

## References
- https://git.kernel.org/stable/c/1a9e02673e2550f5612099e64e8761f0c8fc0f50
- https://git.kernel.org/stable/c/d1b60e7c9fee34eaedf1fc4e0471f75b33f83a4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53261.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53261
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
