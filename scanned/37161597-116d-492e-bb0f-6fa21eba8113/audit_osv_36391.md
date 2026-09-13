# [H] nfc: rawsock: cancel tx_work before socket teardown

## Summary
Severity: High
Advisory: CVE-2026-23372
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23372
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: rawsock: cancel tx_work before socket teardown

In rawsock_release(), cancel any pending tx_work and purge the write
queue before orphaning the socket.  rawsock_tx_work runs on the system
workqueue and calls nfc_data_exchange which dereferences the NCI
device.  Without synchronization, tx_work can race with socket and
device teardown when a process is killed (e.g. by SIGKILL), leading
to use-after-free or leaked references.

Set SEND_SHUTDOWN first so that if tx_work is already running it will
see the flag and skip transmitting, then use cancel_work_sync to wait
for any in-progress execution to finish, and finally purge any
remaining queued skbs.

## References
- https://git.kernel.org/stable/c/3ae592ed91bb4b6b51df256b51045c13d2656049
- https://git.kernel.org/stable/c/722a28b635ec281bb08a23885223526d8e7d6526
- https://git.kernel.org/stable/c/78141b8832e16d80d09cbefb4258612db0777a24
- https://git.kernel.org/stable/c/9b2d23cd09e1cb56bdf0e4d5614703094159f16c
- https://git.kernel.org/stable/c/cdeed45ce8c92defd057f7d67ee9a69374d8fa16
- https://git.kernel.org/stable/c/d793458c45df2aed498d7f74145eab7ee22d25aa
- https://git.kernel.org/stable/c/da4515fc8263c5933ed605e396af91079806dc45
- https://git.kernel.org/stable/c/edc988613def90c5b558e025b1b423f48007be06
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23372.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23372
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
