# [H] char: tlclk: fix use-after-free in tlclk_cleanup()

## Summary
Severity: High
Advisory: CVE-2026-80622
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80622
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

char: tlclk: fix use-after-free in tlclk_cleanup()

This patch improves the module cleanup process in the tlclk driver to
prevent potential use-after-free and race conditions.

Currently, the file_operations structure does not specify the .owner
field, which could allow the module to be unloaded while user-space
processes are still interacting with the device. Additionally, the
tlclk_cleanup() function frees the alarm_events memory before ensuring
that blocked processes in the waitqueue are fully awakened and that the
switchover_timer has completed.

To address these cases, this patch:
- Sets '.owner = THIS_MODULE' in tlclk_fops to safely defer module
  unloading while the device is in use.
- Updates tlclk_cleanup() to explicitly wake up all blocked readers
  (wake_up_all), properly release hardware I/O regions, and safely
  delete the timer (timer_delete_sync) prior to freeing memory.

## References
- https://git.kernel.org/stable/c/09d8d2a46a9ec9ff728f3159a174a2ab25dd0f0a
- https://git.kernel.org/stable/c/166dd1d5265e067459e674c11688919901813ec2
- https://git.kernel.org/stable/c/3d5e4cc0d9dce79b0429da3134ac7b072ab9009f
- https://git.kernel.org/stable/c/42223445607a9a5df3cb1c4729abfe3a5085e7ce
- https://git.kernel.org/stable/c/764723bd67a6c8f53a8d8309211fb039e2ebcf49
- https://git.kernel.org/stable/c/96902299a22d126ef5eb3f45cd5d8ceea9e6a735
- https://git.kernel.org/stable/c/bbf003b7794d6ad6f939fdd29f1f1bde8ac554c1
- https://git.kernel.org/stable/c/c3f0cd76561ae611c2d247ee96dfd559e4197cb7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80622.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80622
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
