# [H] tty: n_gsm: fix race condition in status line change on dead connections

## Summary
Severity: High
Advisory: CVE-2023-52872
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52872
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.138, >=5.16.0 <6.1.62, >=6.0.0 <6.5.11, >=6.2.0 <6.6.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: n_gsm: fix race condition in status line change on dead connections

gsm_cleanup_mux() cleans up the gsm by closing all DLCIs, stopping all
timers, removing the virtual tty devices and clearing the data queues.
This procedure, however, may cause subsequent changes of the virtual modem
status lines of a DLCI. More data is being added the outgoing data queue
and the deleted kick timer is restarted to handle this. At this point many
resources have already been removed by the cleanup procedure. Thus, a
kernel panic occurs.

Fix this by proving in gsm_modem_update() that the cleanup procedure has
not been started and the mux is still alive.

Note that writing to a virtual tty is already protected by checks against
the DLCI specific connection state.

## References
- https://git.kernel.org/stable/c/19d34b73234af542cc8a218cf398dee73cdb1890
- https://git.kernel.org/stable/c/3a75b205de43365f80a33b98ec9289785da56243
- https://git.kernel.org/stable/c/81a4dd5e6c78f5d8952fa8c9d36565db1fe01444
- https://git.kernel.org/stable/c/ce4df90333c4fe65acb8b5089fdfe9b955ce976a
- https://git.kernel.org/stable/c/df6cfab66ff2a44bd23ad5dd5309cb3421bb6593
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52872.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
