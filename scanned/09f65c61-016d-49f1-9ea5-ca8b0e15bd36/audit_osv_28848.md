# [H] thermal/debugfs: Fix two locking issues with thermal zone debug

## Summary
Severity: High
Advisory: CVE-2024-36961
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-03
Source: https://osv.dev/vulnerability/CVE-2024-36961
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal/debugfs: Fix two locking issues with thermal zone debug

With the current thermal zone locking arrangement in the debugfs code,
user space can open the "mitigations" file for a thermal zone before
the zone's debugfs pointer is set which will result in a NULL pointer
dereference in tze_seq_start().

Moreover, thermal_debug_tz_remove() is not called under the thermal
zone lock, so it can run in parallel with the other functions accessing
the thermal zone's struct thermal_debugfs object.  Then, it may clear
tz->debugfs after one of those functions has checked it and the
struct thermal_debugfs object may be freed prematurely.

To address the first problem, pass a pointer to the thermal zone's
struct thermal_debugfs object to debugfs_create_file() in
thermal_debug_tz_add() and make tze_seq_start(), tze_seq_next(),
tze_seq_stop(), and tze_seq_show() retrieve it from s->private
instead of a pointer to the thermal zone object.  This will ensure
that tz_debugfs will be valid across the "mitigations" file accesses
until thermal_debugfs_remove_id() called by thermal_debug_tz_remove()
removes that file.

To address the second problem, use tz->lock in thermal_debug_tz_remove()
around the tz->debugfs value check (in case the same thermal zone is
removed at the same time in two different threads) and its reset to NULL.

Cc :6.8+ <stable@vger.kernel.org> # 6.8+

## References
- https://git.kernel.org/stable/c/6c57bdd0505422d5ccd2df541d993aec978c842e
- https://git.kernel.org/stable/c/c7f7c37271787a7f77d7eedc132b0b419a76b4c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36961.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36961
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
