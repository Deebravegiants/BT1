# [H] Bluetooth: ISO: Fix a use-after-free of the hci_conn pointer

## Summary
Severity: High
Advisory: CVE-2026-53276
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53276
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: Fix a use-after-free of the hci_conn pointer

In iso_sock_rebind_bc(), the bis pointer is cached, then the socket lock is
dropped:
	bis = iso_pi(sk)->conn->hcon;
	/* Release the socket before lookups since that requires hci_dev_lock
	 * which shall not be acquired while holding sock_lock for proper
	 * ordering.
	 */
	release_sock(sk);
	hci_dev_lock(bis->hdev);

During the unlocked window, could a concurrent close() destroy the connection
and free the bis structure, causing hci_dev_lock(bis->hdev) to access memory
after it is freed, fix this by using the hdev reference which was safely
acquired via iso_conn_get_hdev().

## References
- https://git.kernel.org/stable/c/d324b8aa20bd3c3394e3647dc22491d88f3f4e7a
- https://git.kernel.org/stable/c/f50331f2a1441ec49988832c3a95f2edacc47322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53276.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
