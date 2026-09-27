# [H] Bluetooth: hci_event: Fix using rcu_read_(un)lock while iterating

## Summary
Severity: High
Advisory: CVE-2024-56654
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56654
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: Fix using rcu_read_(un)lock while iterating

The usage of rcu_read_(un)lock while inside list_for_each_entry_rcu is
not safe since for the most part entries fetched this way shall be
treated as rcu_dereference:

	Note that the value returned by rcu_dereference() is valid
	only within the enclosing RCU read-side critical section [1]_.
	For example, the following is **not** legal::

		rcu_read_lock();
		p = rcu_dereference(head.next);
		rcu_read_unlock();
		x = p->address;	/* BUG!!! */
		rcu_read_lock();
		y = p->data;	/* BUG!!! */
		rcu_read_unlock();

## References
- https://git.kernel.org/stable/c/0108132d7d76d884e443d18b4f067cdf2811911b
- https://git.kernel.org/stable/c/581dd2dc168fe0ed2a7a5534a724f0d3751c93ae
- https://git.kernel.org/stable/c/f9ecc90b5d501b3a5a62d0685d5104f934bb0104
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56654.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56654
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
