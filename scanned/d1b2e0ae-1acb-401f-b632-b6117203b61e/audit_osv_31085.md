# [H] dm array: fix releasing a faulty array block twice in dm_array_cursor_end

## Summary
Severity: High
Advisory: CVE-2024-57929
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57929
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm array: fix releasing a faulty array block twice in dm_array_cursor_end

When dm_bm_read_lock() fails due to locking or checksum errors, it
releases the faulty block implicitly while leaving an invalid output
pointer behind. The caller of dm_bm_read_lock() should not operate on
this invalid dm_block pointer, or it will lead to undefined result.
For example, the dm_array_cursor incorrectly caches the invalid pointer
on reading a faulty array block, causing a double release in
dm_array_cursor_end(), then hitting the BUG_ON in dm-bufio cache_put().

Reproduce steps:

1. initialize a cache device

dmsetup create cmeta --table "0 8192 linear /dev/sdc 0"
dmsetup create cdata --table "0 65536 linear /dev/sdc 8192"
dmsetup create corig --table "0 524288 linear /dev/sdc $262144"
dd if=/dev/zero of=/dev/mapper/cmeta bs=4k count=1
dmsetup create cache --table "0 524288 cache /dev/mapper/cmeta \
/dev/mapper/cdata /dev/mapper/corig 128 2 metadata2 writethrough smq 0"

2. wipe the second array block offline

dmsteup remove cache cmeta cdata corig
mapping_root=$(dd if=/dev/sdc bs=1c count=8 skip=192 \
2>/dev/null | hexdump -e '1/8 "%u\n"')
ablock=$(dd if=/dev/sdc bs=1c count=8 skip=$((4096*mapping_root+2056)) \
2>/dev/null | hexdump -e '1/8 "%u\n"')
dd if=/dev/zero of=/dev/sdc bs=4k count=1 seek=$ablock

3. try reopen the cache device

dmsetup create cmeta --table "0 8192 linear /dev/sdc 0"
dmsetup create cdata --table "0 65536 linear /dev/sdc 8192"
dmsetup create corig --table "0 524288 linear /dev/sdc $262144"
dmsetup create cache --table "0 524288 cache /dev/mapper/cmeta \
/dev/mapper/cdata /dev/mapper/corig 128 2 metadata2 writethrough smq 0"

Kernel logs:

(snip)
device-mapper: array: array_block_check failed: blocknr 0 != wanted 10
device-mapper: block manager: array validator check failed for block 10
device-mapper: array: get_ablock failed
device-mapper: cache metadata: dm_array_cursor_next for mapping failed
------------[ cut here ]------------
kernel BUG at drivers/md/dm-bufio.c:638!

Fix by setting the cached block pointer to NULL on errors.

In addition to the reproducer described above, this fix can be
verified using the "array_cursor/damaged" test in dm-unit:
  dm-unit run /pdata/array_cursor/damaged --kernel-dir <KERNEL_DIR>

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/017c4470bff53585370028fec9341247bad358ff
- https://git.kernel.org/stable/c/6002bec5354f86d1a2df21468f68e3ec03ede9da
- https://git.kernel.org/stable/c/738994872d77e189b2d13c501a1d145e95d98f46
- https://git.kernel.org/stable/c/9c7c03d0e926762adf3a3a0ba86156fb5e19538b
- https://git.kernel.org/stable/c/e477021d252c007f0c6d45b5d13d341efed03979
- https://git.kernel.org/stable/c/f2893c0804d86230ffb8f1c8703fdbb18648abc8
- https://git.kernel.org/stable/c/fc1ef07c3522e257e32702954f265debbcb096a7
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57929.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57929
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
