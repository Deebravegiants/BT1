# [H] bluetooth/l2cap: sync sock recv cb and release

## Summary
Severity: High
Advisory: CVE-2024-41062
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41062
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

bluetooth/l2cap: sync sock recv cb and release

The problem occurs between the system call to close the sock and hci_rx_work,
where the former releases the sock and the latter accesses it without lock protection.

           CPU0                       CPU1
           ----                       ----
           sock_close                 hci_rx_work
	   l2cap_sock_release         hci_acldata_packet
	   l2cap_sock_kill            l2cap_recv_frame
	   sk_free                    l2cap_conless_channel
	                              l2cap_sock_recv_cb

If hci_rx_work processes the data that needs to be received before the sock is
closed, then everything is normal; Otherwise, the work thread may access the
released sock when receiving data.

Add a chan mutex in the rx callback of the sock to achieve synchronization between
the sock release and recv cb.

Sock is dead, so set chan data to NULL, avoid others use invalid sock pointer.

## References
- https://git.kernel.org/stable/c/3b732449b78183d17178db40be3a4401cf3cd629
- https://git.kernel.org/stable/c/605572e64cd9cebb05ed609d96cff05b50d18cdf
- https://git.kernel.org/stable/c/89e856e124f9ae548572c56b1b70c2255705f8fe
- https://git.kernel.org/stable/c/b803f30ea23e0968b6c8285c42adf0d862ab2bf6
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
