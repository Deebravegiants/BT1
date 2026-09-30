# [H] serial: qcom_geni: fix kfifo underflow when flush precedes DMA completion IRQ

## Summary
Severity: High
Advisory: CVE-2026-63883
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63883
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: qcom_geni: fix kfifo underflow when flush precedes DMA completion IRQ

When uart_flush_buffer() runs before the DMA completion IRQ is delivered,
the following race can occur (all steps serialized by uart_port_lock):

  1. DMA starts: tx_remaining = N, kfifo contains N bytes
  2. DMA completes in hardware; IRQ is pending but not yet delivered
  3. uart_flush_buffer() acquires the port lock and calls kfifo_reset(),
     making kfifo_len() = 0 while tx_remaining remains N
  4. uart_flush_buffer() releases the port lock
  5. DMA IRQ fires; handle_tx_dma() acquires the port lock and calls
     uart_xmit_advance(uport, tx_remaining) on an empty kfifo

uart_xmit_advance() increments kfifo->out by tx_remaining. Since
kfifo_reset() already set both in and out to 0, out wraps past in,
causing kfifo_len() to return UART_XMIT_SIZE - tx_remaining. The next
start_tx_dma() call then submits a DMA transfer of stale buffer data.

Fix this by snapshotting kfifo_len() at the start of handle_tx_dma()
and skipping uart_xmit_advance() when fifo_len < tx_remaining, which
indicates the kfifo was reset by a preceding flush.

## References
- https://git.kernel.org/stable/c/0d2c41a8b00934ddf8a7c1b4cf72dffa1e629c46
- https://git.kernel.org/stable/c/452d6fa37ae9b021f4f6d397dbae077f7296f6f4
- https://git.kernel.org/stable/c/654f45a8569f3cd6ff20bd724a18e0cce65893ba
- https://git.kernel.org/stable/c/b1159dce10b38eb795e4c96cdc4d34b83cec81c5
- https://git.kernel.org/stable/c/c91ea13375f70f6271a0183445e34e83b8f4d8f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63883.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
