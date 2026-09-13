# [H] btrfs: fix qgroup reserve overflow the qgroup limit

## Summary
Severity: High
Advisory: CVE-2022-49075
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49075
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix qgroup reserve overflow the qgroup limit

We use extent_changeset->bytes_changed in qgroup_reserve_data() to record
how many bytes we set for EXTENT_QGROUP_RESERVED state. Currently the
bytes_changed is set as "unsigned int", and it will overflow if we try to
fallocate a range larger than 4GiB. The result is we reserve less bytes
and eventually break the qgroup limit.

Unlike regular buffered/direct write, which we use one changeset for
each ordered extent, which can never be larger than 256M.  For
fallocate, we use one changeset for the whole range, thus it no longer
respects the 256M per extent limit, and caused the problem.

The following example test script reproduces the problem:

  $ cat qgroup-overflow.sh
  #!/bin/bash

  DEV=/dev/sdj
  MNT=/mnt/sdj

  mkfs.btrfs -f $DEV
  mount $DEV $MNT

  # Set qgroup limit to 2GiB.
  btrfs quota enable $MNT
  btrfs qgroup limit 2G $MNT

  # Try to fallocate a 3GiB file. This should fail.
  echo
  echo "Try to fallocate a 3GiB file..."
  fallocate -l 3G $MNT/3G.file

  # Try to fallocate a 5GiB file.
  echo
  echo "Try to fallocate a 5GiB file..."
  fallocate -l 5G $MNT/5G.file

  # See we break the qgroup limit.
  echo
  sync
  btrfs qgroup show -r $MNT

  umount $MNT

When running the test:

  $ ./qgroup-overflow.sh
  (...)

  Try to fallocate a 3GiB file...
  fallocate: fallocate failed: Disk quota exceeded

  Try to fallocate a 5GiB file...

  qgroupid         rfer         excl     max_rfer
  --------         ----         ----     --------
  0/5           5.00GiB      5.00GiB      2.00GiB

Since we have no control of how bytes_changed is used, it's better to
set it to u64.

## References
- https://git.kernel.org/stable/c/0355387ea5b02d353c9415613fab908fac5c52a6
- https://git.kernel.org/stable/c/44277c50fdba5019ca25bfad1b71e2561b0de11b
- https://git.kernel.org/stable/c/4b98799e181b4326a613108cf37acc1f55d21b45
- https://git.kernel.org/stable/c/6bfff81286d4491f02dad7814bae5c77c9ad2320
- https://git.kernel.org/stable/c/7941b74ed49b6db25efbef2256ebef843c11a010
- https://git.kernel.org/stable/c/82ae73ac963cee877ce34f7c31b2b456b516e96c
- https://git.kernel.org/stable/c/b642b52d0b50f4d398cb4293f64992d0eed2e2ce
- https://git.kernel.org/stable/c/f3d97b22a708bf9e3f3ac2ba232bcefd0b0c136b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49075.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
