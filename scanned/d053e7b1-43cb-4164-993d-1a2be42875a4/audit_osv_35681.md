# [M] PL011 UART error interrupts never cleared, enabling an external-peer interrupt-storm denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-12629
Aliases: GHSA-36rp-2hcp-f5hv
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-12629
Type: osv

## Details
The ARM PL011 UART driver in drivers/serial/uart_pl011.c fails to acknowledge receive error interrupts. On the PL011, the framing, parity, break, and overrun error interrupts (PL011_IMSC_ERROR_MASK) are cleared only by writing the interrupt-clear register UARTICR; reading the data register clears the RX interrupt and the per-byte RSR status but not the error interrupt status in MIS. The interrupt service routine pl011_isr() acknowledged only the CTS modem-status interrupt and never wrote icr for the error bits, so an asserted error interrupt remains pending after the ISR returns.

When an application enables error-interrupt reporting via the public uart_irq_err_enable() API, an attacker who controls the serial peer can deterministically assert these error bits by injecting line errors on the RX line — a baud/stop-bit mismatch or mid-character break (framing/break error), a flipped parity bit (parity error), or FIFO flooding (overrun error). Because the error interrupt is never cleared, the interrupt line stays asserted and the CPU re-enters pl011_isr() immediately and indefinitely, producing an interrupt-storm livelock from which the core makes no forward progress.

The impact is an availability-only denial of service (permanent hang), reachable from an external or removable UART peer. Exploitation is gated by configuration: the error interrupt is off by default and no in-tree subsystem enables it, so only applications that explicitly call uart_irq_err_enable() on a PL011-based, interrupt-driven port are affected. The fix makes pl011_isr() acknowledge the pending error bits via uart->icr, breaking the loop, and additionally clears the latched RSR status in pl011_err_check().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12629.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-36rp-2hcp-f5hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-12629
- https://github.com/zephyrproject-rtos/zephyr/commit/1069b6822ac90da2b9e6dc8a5bbe3873e9f92818
- https://github.com/zephyrproject-rtos/zephyr
