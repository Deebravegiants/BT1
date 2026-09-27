# [H] gpib: fix use-after-free in IO ioctl handlers

## Summary
Severity: High
Advisory: CVE-2026-31769
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31769
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpib: fix use-after-free in IO ioctl handlers

The IBRD, IBWRT, IBCMD, and IBWAIT ioctl handlers use a gpib_descriptor
pointer after board->big_gpib_mutex has been released.  A concurrent
IBCLOSEDEV ioctl can free the descriptor via close_dev_ioctl() during
this window, causing a use-after-free.

The IO handlers (read_ioctl, write_ioctl, command_ioctl) explicitly
release big_gpib_mutex before calling their handler.  wait_ioctl() is
called with big_gpib_mutex held, but ibwait() releases it internally
when wait_mask is non-zero.  In all four cases, the descriptor pointer
obtained from handle_to_descriptor() becomes unprotected.

Fix this by introducing a kernel-only descriptor_busy reference count
in struct gpib_descriptor.  Each handler atomically increments
descriptor_busy under file_priv->descriptors_mutex before releasing the
lock, and decrements it when done.  close_dev_ioctl() checks
descriptor_busy under the same lock and rejects the close with -EBUSY
if the count is non-zero.

A reference count rather than a simple flag is necessary because
multiple handlers can operate on the same descriptor concurrently
(e.g. IBRD and IBWAIT on the same handle from different threads).

A separate counter is needed because io_in_progress can be cleared from
unprivileged userspace via the IBWAIT ioctl (through general_ibstatus()
with set_mask containing CMPL), which would allow an attacker to bypass
a check based solely on io_in_progress.  The new descriptor_busy
counter is only modified by the kernel IO paths.

The lock ordering is consistent (big_gpib_mutex -> descriptors_mutex)
and the handlers only hold descriptors_mutex briefly during the lookup,
so there is no deadlock risk and no impact on IO throughput.

## References
- https://git.kernel.org/stable/c/28c75dd143ead62e0dfac564c79d251e21d5d74b
- https://git.kernel.org/stable/c/cae26eff1b56d78bed7873cf3e60a2b1bdd4da6c
- https://git.kernel.org/stable/c/d1857f8296dceb75d00ab857fc3c61bc00c7f5c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31769.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31769
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
