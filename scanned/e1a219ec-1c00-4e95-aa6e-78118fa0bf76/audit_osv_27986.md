# [H] binder: check offset alignment in binder_get_object()

## Summary
Severity: High
Advisory: CVE-2024-26926
Aliases: A-320661088, ASB-A-320661088
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-24
Source: https://osv.dev/vulnerability/CVE-2024-26926
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.157, >=5.16.0 <6.1.88, >=5.17.0 <6.6.29, >=6.2.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: check offset alignment in binder_get_object()

Commit 6d98eb95b450 ("binder: avoid potential data leakage when copying
txn") introduced changes to how binder objects are copied. In doing so,
it unintentionally removed an offset alignment check done through calls
to binder_alloc_copy_from_buffer() -> check_buffer().

These calls were replaced in binder_get_object() with copy_from_user(),
so now an explicit offset alignment check is needed here. This avoids
later complications when unwinding the objects gets harder.

It is worth noting this check existed prior to commit 7a67a39320df
("binder: add function to copy binder object from buffer"), likely
removed due to redundancy at the time.

## References
- https://git.kernel.org/stable/c/1d7f1049035b2060342f11eff957cf567d810bdc
- https://git.kernel.org/stable/c/48a1f83ca9c68518b1a783c62e6a8223144fa9fc
- https://git.kernel.org/stable/c/68a28f551e4690db2b27b3db716c7395f6fada12
- https://git.kernel.org/stable/c/a2fd6dbc98be1105a1d8e9e31575da8873ef115c
- https://git.kernel.org/stable/c/a6d2a8b211c874971ee4cf3ddd167408177f6e76
- https://git.kernel.org/stable/c/aaef73821a3b0194a01bd23ca77774f704a04d40
- https://git.kernel.org/stable/c/f01d6619045704d78613b14e2e0420bfdb7f1c15
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26926.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
