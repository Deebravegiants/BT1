# [H] USB: dummy-hcd: Fix interrupt synchronization error

## Summary
Severity: High
Advisory: CVE-2026-43324
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43324
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: dummy-hcd: Fix interrupt synchronization error

This fixes an error in synchronization in the dummy-hcd driver.  The
error has a somewhat involved history.  The synchronization mechanism
was introduced by commit 7dbd8f4cabd9 ("USB: dummy-hcd: Fix erroneous
synchronization change"), which added an emulated "interrupts enabled"
flag together with code emulating synchronize_irq() (it waits until
all current handler callbacks have returned).

But the emulated interrupt-disable occurred too late, after the driver
containing the handler callback routines had been told that it was
unbound and no more callbacks would occur.  Commit 4a5d797a9f9c ("usb:
gadget: dummy_hcd: fix gpf in gadget_setup") tried to fix this by
moving the synchronize_irq() emulation code from dummy_stop() to
dummy_pullup(), which runs before the unbind callback.

There still were races, though, because the emulated interrupt-disable
still occurred too late.  It couldn't be moved to dummy_pullup(),
because that routine can be called for reasons other than an impending
unbind.  Therefore commits 7dc0c55e9f30 ("USB: UDC core: Add
udc_async_callbacks gadget op") and 04145a03db9d ("USB: UDC: Implement
udc_async_callbacks in dummy-hcd") added an API allowing the UDC core
to tell dummy-hcd exactly when emulated interrupts and their callbacks
should be disabled.

That brings us to the current state of things, which is still wrong
because the emulated synchronize_irq() occurs before the emulated
interrupt-disable!  That's no good, beause it means that more emulated
interrupts can occur after the synchronize_irq() emulation has run,
leading to the possibility that a callback handler may be running when
the gadget driver is unbound.

To fix this, we have to move the synchronize_irq() emulation code yet
again, to the dummy_udc_async_callbacks() routine, which takes care of
enabling and disabling emulated interrupt requests.  The
synchronization will now run immediately after emulated interrupts are
disabled, which is where it belongs.

## References
- https://git.kernel.org/stable/c/2ca9e46f8f1f5a297eb0ac83f79d35d5b3a02541
- https://git.kernel.org/stable/c/5687a09776069bd915560021c9728ca528440128
- https://git.kernel.org/stable/c/5aa776c8615bea3b1eaeec87b0788375800ead4f
- https://git.kernel.org/stable/c/8bcd80219d8e10e660bf29b20e41bb8beb4e4cb7
- https://git.kernel.org/stable/c/94d4fab1dd9e64f45449bcc7d6a5acf796b13015
- https://git.kernel.org/stable/c/cbf7df5e5d27cd5bea92ee9a75a4b28dbcc718d4
- https://git.kernel.org/stable/c/d847f375b1bcea713143bc02720d13d2d01b012a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43324.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43324
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
