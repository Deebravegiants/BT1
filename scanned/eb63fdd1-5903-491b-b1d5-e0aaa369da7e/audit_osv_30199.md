# [H] drm/panthor: Fix race when converting group handle to group object

## Summary
Severity: High
Advisory: CVE-2024-50174
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50174
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Fix race when converting group handle to group object

XArray provides it's own internal lock which protects the internal array
when entries are being simultaneously added and removed. However there
is still a race between retrieving the pointer from the XArray and
incrementing the reference count.

To avoid this race simply hold the internal XArray lock when
incrementing the reference count, this ensures there cannot be a racing
call to xa_erase().

## References
- https://git.kernel.org/stable/c/44742138d151c3a945460ae7beff8ae45ac0bf58
- https://git.kernel.org/stable/c/8a585d553c11965332d7a2d74e79ef92a42bfc87
- https://git.kernel.org/stable/c/cac075706f298948898b1f63e81709df42afa75d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50174.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50174
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
