# [H] zram: fix slot write race condition

## Summary
Severity: High
Advisory: CVE-2025-39941
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39941
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

zram: fix slot write race condition

Parallel concurrent writes to the same zram index result in leaked
zsmalloc handles.  Schematically we can have something like this:

CPU0                              CPU1
zram_slot_lock()
zs_free(handle)
zram_slot_lock()
				zram_slot_lock()
				zs_free(handle)
				zram_slot_lock()

compress			compress
handle = zs_malloc()		handle = zs_malloc()
zram_slot_lock
zram_set_handle(handle)
zram_slot_lock
				zram_slot_lock
				zram_set_handle(handle)
				zram_slot_lock

Either CPU0 or CPU1 zsmalloc handle will leak because zs_free() is done
too early.  In fact, we need to reset zram entry right before we set its
new handle, all under the same slot lock scope.

## References
- https://git.kernel.org/stable/c/ce4be9e4307c5a60701ff6e0cafa74caffdc54ce
- https://git.kernel.org/stable/c/ff750e9f2c4d63854c33967d1646b5e89a9a19a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39941.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39941
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
