# [H] Bluetooth: btnxpuart: Resolve TX timeout error in power save stress test

## Summary
Severity: High
Advisory: CVE-2024-58238
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-08-09
Source: https://osv.dev/vulnerability/CVE-2024-58238
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.49

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btnxpuart: Resolve TX timeout error in power save stress test

This fixes the tx timeout issue seen while running a stress test on
btnxpuart for couple of hours, such that the interval between two HCI
commands coincide with the power save timeout value of 2 seconds.

Test procedure using bash script:
<load btnxpuart.ko>
hciconfig hci0 up
//Enable Power Save feature
hcitool -i hci0 cmd 3f 23 02 00 00
while (true)
do
    hciconfig hci0 leadv
    sleep 2
    hciconfig hci0 noleadv
    sleep 2
done

Error log, after adding few more debug prints:
Bluetooth: btnxpuart_queue_skb(): 01 0A 20 01 00
Bluetooth: hci0: Set UART break: on, status=0
Bluetooth: hci0: btnxpuart_tx_wakeup() tx_work scheduled
Bluetooth: hci0: btnxpuart_tx_work() dequeue: 01 0A 20 01 00
Can't set advertise mode on hci0: Connection timed out (110)
Bluetooth: hci0: command 0x200a tx timeout

When the power save mechanism turns on UART break, and btnxpuart_tx_work()
is scheduled simultaneously, psdata->ps_state is read as PS_STATE_AWAKE,
which prevents the psdata->work from being scheduled, which is responsible
to turn OFF UART break.

This issue is fixed by adding a ps_lock mutex around UART break on/off as
well as around ps_state read/write.
btnxpuart_tx_wakeup() will now read updated ps_state value. If ps_state is
PS_STATE_SLEEP, it will first schedule psdata->work, and then it will
reschedule itself once UART break has been turned off and ps_state is
PS_STATE_AWAKE.

Tested above script for 50,000 iterations and TX timeout error was not
observed anymore.

## References
- https://git.kernel.org/stable/c/9d5df94ce0e213d5b549633f528f96114c736190
- https://git.kernel.org/stable/c/e4db90e4eb8d5487098712ffb1048f3fa6d25e98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58238.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58238
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
