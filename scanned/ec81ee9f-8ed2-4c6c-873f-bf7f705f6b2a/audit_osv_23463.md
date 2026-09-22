# [H] tty: serial: qcom-geni-serial: fix slab-out-of-bounds on RX FIFO buffer

## Summary
Severity: High
Advisory: CVE-2022-48871
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2022-48871
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.165, >=5.11.0 <5.15.90, >=5.16.0 <6.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: serial: qcom-geni-serial: fix slab-out-of-bounds on RX FIFO buffer

Driver's probe allocates memory for RX FIFO (port->rx_fifo) based on
default RX FIFO depth, e.g. 16.  Later during serial startup the
qcom_geni_serial_port_setup() updates the RX FIFO depth
(port->rx_fifo_depth) to match real device capabilities, e.g. to 32.

The RX UART handle code will read "port->rx_fifo_depth" number of words
into "port->rx_fifo" buffer, thus exceeding the bounds.  This can be
observed in certain configurations with Qualcomm Bluetooth HCI UART
device and KASAN:

  Bluetooth: hci0: QCA Product ID   :0x00000010
  Bluetooth: hci0: QCA SOC Version  :0x400a0200
  Bluetooth: hci0: QCA ROM Version  :0x00000200
  Bluetooth: hci0: QCA Patch Version:0x00000d2b
  Bluetooth: hci0: QCA controller version 0x02000200
  Bluetooth: hci0: QCA Downloading qca/htbtfw20.tlv
  bluetooth hci0: Direct firmware load for qca/htbtfw20.tlv failed with error -2
  Bluetooth: hci0: QCA Failed to request file: qca/htbtfw20.tlv (-2)
  Bluetooth: hci0: QCA Failed to download patch (-2)
  ==================================================================
  BUG: KASAN: slab-out-of-bounds in handle_rx_uart+0xa8/0x18c
  Write of size 4 at addr ffff279347d578c0 by task swapper/0/0

  CPU: 0 PID: 0 Comm: swapper/0 Not tainted 6.1.0-rt5-00350-gb2450b7e00be-dirty #26
  Hardware name: Qualcomm Technologies, Inc. Robotics RB5 (DT)
  Call trace:
   dump_backtrace.part.0+0xe0/0xf0
   show_stack+0x18/0x40
   dump_stack_lvl+0x8c/0xb8
   print_report+0x188/0x488
   kasan_report+0xb4/0x100
   __asan_store4+0x80/0xa4
   handle_rx_uart+0xa8/0x18c
   qcom_geni_serial_handle_rx+0x84/0x9c
   qcom_geni_serial_isr+0x24c/0x760
   __handle_irq_event_percpu+0x108/0x500
   handle_irq_event+0x6c/0x110
   handle_fasteoi_irq+0x138/0x2cc
   generic_handle_domain_irq+0x48/0x64

If the RX FIFO depth changes after probe, be sure to resize the buffer.

## References
- https://git.kernel.org/stable/c/894681682dbefdad917b88f86cde1069140a047a
- https://git.kernel.org/stable/c/b8caf69a6946e18ffebad49847e258f5b6d52ac2
- https://git.kernel.org/stable/c/cb53a3366eb28fed67850c80afa52075bb71a38a
- https://git.kernel.org/stable/c/fd524ca7fe45b8a06dca2dd546d62684a9768f95
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48871.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48871
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
