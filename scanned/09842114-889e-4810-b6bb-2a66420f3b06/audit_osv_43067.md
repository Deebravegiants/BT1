# [H] net: mvneta: re-enable percpu interrupt on resume

## Summary
Severity: High
Advisory: CVE-2026-72409
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72409
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mvneta: re-enable percpu interrupt on resume

On Marvell MPIC platforms (Armada 370/XP/38x), mvneta uses a percpu
IRQ disable/enable scheme for NAPI: the ISR (mvneta_percpu_isr) calls
disable_percpu_irq() to mask the MPIC per-CPU interrupt and schedules
NAPI poll, which calls enable_percpu_irq() on completion to unmask.

If suspend occurs while NAPI poll is pending (between
disable_percpu_irq in the ISR and enable_percpu_irq in poll
completion), the interrupt is never re-enabled:

  1. mvneta_percpu_isr: disable_percpu_irq() + napi_schedule()
     => MPIC masked, percpu_enabled cpumask bit cleared
  2. NAPI poll does not complete before suspend proceeds
     (on PREEMPT_RT this is highly likely since softirqs run in
     ksoftirqd which gets frozen; on non-RT it can happen when
     softirq processing is deferred to ksoftirqd)
  3. mvneta_stop_dev => napi_disable(): cancels the pending poll
     without executing the completion path
  4. suspend_device_irqs => IRQCHIP_MASK_ON_SUSPEND: masks MPIC
     (already masked, but records IRQS_SUSPENDED)
  5. Resume: mpic_resume checks irq_percpu_is_enabled() => false
     (bit was cleared in step 1) => skips unmask
  6. mvneta_start_dev only restores device-level INTR_NEW_MASK,
     does not touch the MPIC per-CPU mask

Result: MPIC per-CPU interrupt stays masked permanently. The NIC
generates interrupts (INTR_NEW_CAUSE != 0) but the CPU never
receives them, causing complete loss of network connectivity.

Fix by calling on_each_cpu(mvneta_percpu_enable) in the resume path
to unconditionally unmask the MPIC per-CPU interrupt regardless of
pre-suspend state.

## References
- https://git.kernel.org/stable/c/1cc312dc8bc78fa24c80d5bc193dbf5b57a99cc6
- https://git.kernel.org/stable/c/5bdb33ff6e58bdc43632e98b30723eb65352d671
- https://git.kernel.org/stable/c/82c13027ed283b856017adee970dbfdffce5c6b8
- https://git.kernel.org/stable/c/8c7a489aa71d2693752b2e794a68bf672d16c829
- https://git.kernel.org/stable/c/b84dd48f9da1eb132bdc06a944423cd5a1641ef1
- https://git.kernel.org/stable/c/be626ac1faadd49c2cead9f9cd06ba8752d81563
- https://git.kernel.org/stable/c/bf88cd3b649bc3e638f1e8a77649581852747a68
- https://git.kernel.org/stable/c/fd398d6480987e4c84fff0aaab6b9d6642a93343
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72409.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72409
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
