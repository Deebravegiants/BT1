# [M] CVE-2021-47119

## Summary
Severity: Medium
Advisory: CVE-2021-47119
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47119
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix memory leak in ext4_fill_super

Buffer head references must be released before calling kill_bdev();
otherwise the buffer head (and its page referenced by b_data) will not
be freed by kill_bdev, and subsequently that bh will be leaked.

If blocksizes differ, sb_set_blocksize() will kill current buffers and
page cache by using kill_bdev(). And then super block will be reread
again but using correct blocksize this time. sb_set_blocksize() didn't
fully free superblock page and buffer head, and being busy, they were
not freed and instead leaked.

This can easily be reproduced by calling an infinite loop of:

  systemctl start <ext4_on_lvm>.mount, and
  systemctl stop <ext4_on_lvm>.mount

... since systemd creates a cgroup for each slice which it mounts, and
the bh leak get amplified by a dying memory cgroup that also never
gets freed, and memory consumption is much more easily noticed.

## References
- https://git.kernel.org/stable/c/01d349a481f0591230300a9171330136f9159bcd
- https://git.kernel.org/stable/c/1385b23396d511d5233b8b921ac3058b3f86a5e1
- https://git.kernel.org/stable/c/afd09b617db3786b6ef3dc43e28fe728cfea84df
