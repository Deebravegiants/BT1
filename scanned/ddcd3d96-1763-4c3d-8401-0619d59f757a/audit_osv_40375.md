# [M] dm log: fix out-of-bounds write due to region_count overflow

## Summary
Severity: Medium
Advisory: CVE-2026-53059
Ecosystem: Linux
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53059
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm log: fix out-of-bounds write due to region_count overflow

The local variable region_count in create_log_context() is declared as
unsigned int (32-bit), but dm_sector_div_up() returns sector_t (64-bit).
When a device-mapper target has a sufficiently large ti->len with a small
region_size, the division result can exceed UINT_MAX. The truncated
value is then used to calculate bitset_size, causing clean_bits,
sync_bits, and recovering_bits to be allocated far smaller than needed
for the actual number of regions.

Subsequent log operations (log_set_bit, log_clear_bit, log_test_bit) use
region indices derived from the full untruncated region space, causing
out-of-bounds writes to kernel heap memory allocated by vmalloc.

This can be reproduced by creating a mirror target whose region_count
overflows 32 bits:

  dmsetup create bigzero --table '0 8589934594 zero'
  dmsetup create mymirror --table '0 8589934594 mirror \
    core 2 2 nosync 2 /dev/mapper/bigzero 0 \
    /dev/mapper/bigzero 0'

The status output confirms the truncation (sync_count=1 instead of
4294967297, because 0x100000001 was truncated to 1):

  $ dmsetup status mymirror
  0 8589934594 mirror 2 254:1 254:1 1/4294967297 ...

This leads to a kernel crash in core_in_sync:

  BUG: scheduling while atomic: (udev-worker)/9150/0x00000000
  RIP: 0010:core_in_sync+0x14/0x30 [dm_log]
  CR2: 0000000000000008
  Fixing recursive fault but reboot is needed!

Fix by widening the local region_count to sector_t and adding an
explicit overflow check before the value is assigned to lc->region_count.

## References
- https://git.kernel.org/stable/c/12bd5b88e91a02785244ff1d20fb157e96e9cdc8
- https://git.kernel.org/stable/c/3ec74da927b4e171a6fc0e77b1188ba4d019af51
- https://git.kernel.org/stable/c/44ab8875ae4a2842bde2d756bed195d375e0debb
- https://git.kernel.org/stable/c/4ec8323b9f0764a14d532b1ae9b87f8a9fecb867
- https://git.kernel.org/stable/c/b455903eed4558982be0811f5b7f44f6bbc4ff57
- https://git.kernel.org/stable/c/c20e36b7631d83e7535877f08af8b0af72c44b1a
- https://git.kernel.org/stable/c/d4ac87567f86a55c3c92e9a5144dcd943a9772a1
- https://git.kernel.org/stable/c/defe483e47173768c227532694dc78cb65db5f09
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53059.json
- https://access.redhat.com/errata/RHSA-2026:45114
- https://access.redhat.com/errata/RHSA-2026:45115
- https://access.redhat.com/errata/RHSA-2026:45116
- https://access.redhat.com/errata/RHSA-2026:45192
- https://access.redhat.com/errata/RHSA-2026:47248
- https://access.redhat.com/errata/RHSA-2026:52649
- https://access.redhat.com/errata/RHSA-2026:53989
- https://access.redhat.com/errata/RHSA-2026:55445
- https://access.redhat.com/errata/RHSA-2026:56574
- https://access.redhat.com/errata/RHSA-2026:59662
- https://access.redhat.com/errata/RHSA-2026:59663
