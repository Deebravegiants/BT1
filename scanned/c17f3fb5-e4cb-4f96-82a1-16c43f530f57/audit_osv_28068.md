# [H] pstore: inode: Only d_invalidate() is needed

## Summary
Severity: High
Advisory: CVE-2024-27389
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27389
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.15.209, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

pstore: inode: Only d_invalidate() is needed

Unloading a modular pstore backend with records in pstorefs would
trigger the dput() double-drop warning:

  WARNING: CPU: 0 PID: 2569 at fs/dcache.c:762 dput.part.0+0x3f3/0x410

Using the combo of d_drop()/dput() (as mentioned in
Documentation/filesystems/vfs.rst) isn't the right approach here, and
leads to the reference counting problem seen above. Use d_invalidate()
and update the code to not bother checking for error codes that can
never happen.

---

## References
- https://git.kernel.org/stable/c/340682ed1932b8e3bd0bfc6c31a0c6354eb57cc6
- https://git.kernel.org/stable/c/4cdf9006fc095af71da80e9b5f48a32e991b9ed3
- https://git.kernel.org/stable/c/a43e0fc5e9134a46515de2f2f8d4100b74e50de3
- https://git.kernel.org/stable/c/cb9e802e49c24eeb3af35e9e8c04d526f35f112a
- https://git.kernel.org/stable/c/d0ee2a8adb6673382cce8a4280e1ca0849b3b783
- https://git.kernel.org/stable/c/db6e5e16f1ee9e3b01d2f71c7f0ba945f4bf0f4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27389.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
