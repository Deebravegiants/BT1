# [H] hwmon: (nzxt-smart2) DMA-align output buffer

## Summary
Severity: High
Advisory: CVE-2026-74551
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74551
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (nzxt-smart2) DMA-align output buffer

Sashiko reports:

When send_output_report() calls hid_hw_output_report(), the underlying USB
HID core calls usb_interrupt_msg() which maps this buffer directly for DMA.

When the DMA mapping flushes or invalidates the cacheline, it will corrupt
the adjacent variables (mutex, update_interval) that were modified
concurrently by the CPU. This causes memory corruption due to cacheline
sharing on non-coherent CPU architectures (such as ARM or MIPS). The DMA
API debugging tool (CONFIG_DMA_API_DEBUG) will trigger runtime warnings
for this violation.

Any operation that triggers send_output_report() (like setting a fan speed
or updating the interval) causes the USB DMA mapping. On systems with
non-coherent caches, this structural bug causes immediate and deterministic
memory corruption.

Align the output buffer to ARCH_DMA_MINALIGN to fix the problem.

## References
- https://git.kernel.org/stable/c/080bbf42faf77e6489ab30d5114c5f8f6ccbb1b8
- https://git.kernel.org/stable/c/2332d35aaf206c17acf848522817252732596676
- https://git.kernel.org/stable/c/51a76bc1b8e717ee3fc0d84f15ac51490ca5f76f
- https://git.kernel.org/stable/c/6a2dbce5da2d2163a5b684acf68a0e54582ff0fa
- https://git.kernel.org/stable/c/70ad543ce81f368411b6c721265a3b2d7ab4fda4
- https://git.kernel.org/stable/c/81a6593b1c8dfb2694cd0ce39be01212d2b8436c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74551.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74551
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
