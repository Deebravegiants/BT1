# [H] Bluetooth: hci_qca: Clear memdump state on invalid dump size

## Summary
Severity: High
Advisory: CVE-2026-68389
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68389
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_qca: Clear memdump state on invalid dump size

qca_controller_memdump() allocates qca->qca_memdump before processing
the first dump packet. For a sequence-zero packet it then disables IBS,
marks memdump collection active, and reads the advertised dump size.

If the controller reports a zero dump size, the error path frees the
local qca_memdump object and returns without clearing qca->qca_memdump
or undoing the collection state. A later memdump work item initializes
its local pointer from qca->qca_memdump and skips allocation when that
pointer is non-NULL, so it can operate on freed memory. The stale
collection and IBS-disabled flags can also leave waiters or later
transmit handling blocked behind an aborted dump.

Clear the saved pointer and memdump state before returning from the
invalid-size path, matching the cleanup used when hci_devcd_init() fails.

A static analysis checker reported the stale memdump state, and manual
source review confirmed the invalid-size failure path.

## References
- https://git.kernel.org/stable/c/069258d5111eed9ac9586bee42d03d38e2975715
- https://git.kernel.org/stable/c/2363a757694752426fc47f3eadde15cf5f791fa5
- https://git.kernel.org/stable/c/5a3945e8dea6c9a8ec9e981169ac9487e1d6ad6a
- https://git.kernel.org/stable/c/bf587a10c33e5571a299742e45bc18960b9912e7
- https://git.kernel.org/stable/c/cefb44c367b2b52e50f97bc8526d39df9bcf5e60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68389.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
