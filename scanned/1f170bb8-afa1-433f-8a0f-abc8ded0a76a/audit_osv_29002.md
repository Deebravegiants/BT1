# [H] ALSA: core: Fix NULL module pointer assignment at card init

## Summary
Severity: High
Advisory: CVE-2024-38605
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38605
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: core: Fix NULL module pointer assignment at card init

The commit 81033c6b584b ("ALSA: core: Warn on empty module")
introduced a WARN_ON() for a NULL module pointer passed at snd_card
object creation, and it also wraps the code around it with '#ifdef
MODULE'.  This works in most cases, but the devils are always in
details.  "MODULE" is defined when the target code (i.e. the sound
core) is built as a module; but this doesn't mean that the caller is
also built-in or not.  Namely, when only the sound core is built-in
(CONFIG_SND=y) while the driver is a module (CONFIG_SND_USB_AUDIO=m),
the passed module pointer is ignored even if it's non-NULL, and
card->module remains as NULL.  This would result in the missing module
reference up/down at the device open/close, leading to a race with the
code execution after the module removal.

For addressing the bug, move the assignment of card->module again out
of ifdef.  The WARN_ON() is still wrapped with ifdef because the
module can be really NULL when all sound drivers are built-in.

Note that we keep 'ifdef MODULE' for WARN_ON(), otherwise it would
lead to a false-positive NULL module check.  Admittedly it won't catch
perfectly, i.e. no check is performed when CONFIG_SND=y.  But, it's no
real problem as it's only for debugging, and the condition is pretty
rare.

## References
- https://git.kernel.org/stable/c/39381fe7394e5eafac76e7e9367e7351138a29c1
- https://git.kernel.org/stable/c/6b8374ee2cabcf034faa34e69a855dc496a9ec12
- https://git.kernel.org/stable/c/c935e72139e6d523defd60fe875c01eb1f9ea5c5
- https://git.kernel.org/stable/c/d7ff29a429b56f04783152ad7bbd7233b740e434
- https://git.kernel.org/stable/c/e007476725730c1a68387b54b7629486d8a8301e
- https://git.kernel.org/stable/c/e644036a3e2b2c9b3eee3c61b5d31c2ca8b5ba92
- https://git.kernel.org/stable/c/e7e0ca200772bdb2fdc6d43d32d341e87a36f811
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38605.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38605
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
