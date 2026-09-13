# [M] tty: fix deadlock caused by calling printk() under tty_port->lock

## Summary
Severity: Medium
Advisory: CVE-2022-49441
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49441
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.18.0 <5.4.198, >=4.20.0 <5.10.121, >=5.5.0 <5.15.46, >=5.11.0 <5.17.14, >=5.16.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: fix deadlock caused by calling printk() under tty_port->lock

pty_write() invokes kmalloc() which may invoke a normal printk() to print
failure message.  This can cause a deadlock in the scenario reported by
syz-bot below:

       CPU0              CPU1                    CPU2
       ----              ----                    ----
                         lock(console_owner);
                                                 lock(&port_lock_key);
  lock(&port->lock);
                         lock(&port_lock_key);
                                                 lock(&port->lock);
  lock(console_owner);

As commit dbdda842fe96 ("printk: Add console owner and waiter logic to
load balance console writes") said, such deadlock can be prevented by
using printk_deferred() in kmalloc() (which is invoked in the section
guarded by the port->lock).  But there are too many printk() on the
kmalloc() path, and kmalloc() can be called from anywhere, so changing
printk() to printk_deferred() is too complicated and inelegant.

Therefore, this patch chooses to specify __GFP_NOWARN to kmalloc(), so
that printk() will not be called, and this deadlock problem can be
avoided.

Syzbot reported the following lockdep error:

======================================================
WARNING: possible circular locking dependency detected
5.4.143-00237-g08ccc19a-dirty #10 Not tainted
------------------------------------------------------
syz-executor.4/29420 is trying to acquire lock:
ffffffff8aedb2a0 (console_owner){....}-{0:0}, at: console_trylock_spinning kernel/printk/printk.c:1752 [inline]
ffffffff8aedb2a0 (console_owner){....}-{0:0}, at: vprintk_emit+0x2ca/0x470 kernel/printk/printk.c:2023

but task is already holding lock:
ffff8880119c9158 (&port->lock){-.-.}-{2:2}, at: pty_write+0xf4/0x1f0 drivers/tty/pty.c:120

which lock already depends on the new lock.

the existing dependency chain (in reverse order) is:

-> #2 (&port->lock){-.-.}-{2:2}:
       __raw_spin_lock_irqsave include/linux/spinlock_api_smp.h:110 [inline]
       _raw_spin_lock_irqsave+0x35/0x50 kernel/locking/spinlock.c:159
       tty_port_tty_get drivers/tty/tty_port.c:288 [inline]          		<-- lock(&port->lock);
       tty_port_default_wakeup+0x1d/0xb0 drivers/tty/tty_port.c:47
       serial8250_tx_chars+0x530/0xa80 drivers/tty/serial/8250/8250_port.c:1767
       serial8250_handle_irq.part.0+0x31f/0x3d0 drivers/tty/serial/8250/8250_port.c:1854
       serial8250_handle_irq drivers/tty/serial/8250/8250_port.c:1827 [inline] 	<-- lock(&port_lock_key);
       serial8250_default_handle_irq+0xb2/0x220 drivers/tty/serial/8250/8250_port.c:1870
       serial8250_interrupt+0xfd/0x200 drivers/tty/serial/8250/8250_core.c:126
       __handle_irq_event_percpu+0x109/0xa50 kernel/irq/handle.c:156
       [...]

-> #1 (&port_lock_key){-.-.}-{2:2}:
       __raw_spin_lock_irqsave include/linux/spinlock_api_smp.h:110 [inline]
       _raw_spin_lock_irqsave+0x35/0x50 kernel/locking/spinlock.c:159
       serial8250_console_write+0x184/0xa40 drivers/tty/serial/8250/8250_port.c:3198
										<-- lock(&port_lock_key);
       call_console_drivers kernel/printk/printk.c:1819 [inline]
       console_unlock+0x8cb/0xd00 kernel/printk/printk.c:2504
       vprintk_emit+0x1b5/0x470 kernel/printk/printk.c:2024			<-- lock(console_owner);
       vprintk_func+0x8d/0x250 kernel/printk/printk_safe.c:394
       printk+0xba/0xed kernel/printk/printk.c:2084
       register_console+0x8b3/0xc10 kernel/printk/printk.c:2829
       univ8250_console_init+0x3a/0x46 drivers/tty/serial/8250/8250_core.c:681
       console_init+0x49d/0x6d3 kernel/printk/printk.c:2915
       start_kernel+0x5e9/0x879 init/main.c:713
       secondary_startup_64+0xa4/0xb0 arch/x86/kernel/head_64.S:241

-> #0 (console_owner){....}-{0:0}:
       [...]
       lock_acquire+0x127/0x340 kernel/locking/lockdep.c:4734
       console_trylock_spinning kernel/printk/printk.c:1773 
---truncated---

## References
- https://git.kernel.org/stable/c/04ee31678c128a6cc7bb057ea189a8624ba5a314
- https://git.kernel.org/stable/c/0bcf44903ef4df742dcada86ccaedd25374ffb50
- https://git.kernel.org/stable/c/18ca0d55e8639b911df8aae1b47598b13f9acded
- https://git.kernel.org/stable/c/3219ac364ac3d8d30771612a6010f1e0b7fa0a28
- https://git.kernel.org/stable/c/4af21b12a60ed2d3642284f4f85b42d7dc6ac246
- https://git.kernel.org/stable/c/4c253caf9264d2aa47ee806a87986dd8eb91a5d9
- https://git.kernel.org/stable/c/6b9dbedbe3499fef862c4dff5217cf91f34e43b3
- https://git.kernel.org/stable/c/9834b13e8b962caa28fbcf1f422dd82413da4ede
- https://git.kernel.org/stable/c/b3c974501d0c32258ae0e04e5cc3fb92383b40f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49441.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49441
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
