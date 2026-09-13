# [H] atm: fore200e: fix use-after-free in tasklets during device removal

## Summary
Severity: High
Advisory: CVE-2026-43203
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43203
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

atm: fore200e: fix use-after-free in tasklets during device removal

When the PCA-200E or SBA-200E adapter is being detached, the fore200e
is deallocated. However, the tx_tasklet or rx_tasklet may still be running
or pending, leading to use-after-free bug when the already freed fore200e
is accessed again in fore200e_tx_tasklet() or fore200e_rx_tasklet().

One of the race conditions can occur as follows:

CPU 0 (cleanup)           | CPU 1 (tasklet)
fore200e_pca_remove_one() | fore200e_interrupt()
  fore200e_shutdown()     |   tasklet_schedule()
    kfree(fore200e)       | fore200e_tx_tasklet()
                          |   fore200e-> // UAF

Fix this by ensuring tx_tasklet or rx_tasklet is properly canceled before
the fore200e is released. Add tasklet_kill() in fore200e_shutdown() to
synchronize with any pending or running tasklets. Moreover, since
fore200e_reset() could prevent further interrupts or data transfers,
the tasklet_kill() should be placed after fore200e_reset() to prevent
the tasklet from being rescheduled in fore200e_interrupt(). Finally,
it only needs to do tasklet_kill() when the fore200e state is greater
than or equal to FORE200E_STATE_IRQ, since tasklets are uninitialized
in earlier states. In a word, the tasklet_kill() should be placed in
the FORE200E_STATE_IRQ branch within the switch...case structure.

This bug was identified through static analysis.

## References
- https://git.kernel.org/stable/c/5189368f10903956be05062d160b2804bf5e5016
- https://git.kernel.org/stable/c/73fbc5d1a9ccb626937500bbd67136f077d8237b
- https://git.kernel.org/stable/c/8930878101cd40063888a68af73b1b0f8b6c79bc
- https://git.kernel.org/stable/c/91f25749aaf57c47ae1e12478144e6ea8c8562f2
- https://git.kernel.org/stable/c/97900f512252a59f23d6ce4ab215cc88fed66e68
- https://git.kernel.org/stable/c/aba0b4bc09376dfc3d53c826514fe38fc8337f52
- https://git.kernel.org/stable/c/e075ec9b08f862dade8011481058f7eb5f716c57
- https://git.kernel.org/stable/c/e4ff4e3ffcf9d5aad380cdd1d8cdc008bb34f97d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43203.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43203
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
