# [H] Bluetooth: ISO: ensure no dangling hcon references in iso_conn

## Summary
Severity: High
Advisory: CVE-2026-80721
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80721
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: ensure no dangling hcon references in iso_conn

After iso_conn_del(), ISO sockets should not dereference the hcon any
more.  Currently, clearing iso_conn::hcon relies on iso_conn_del()
releasing the last reference to the iso_conn.

Simplify this by explicitly clearing conn->hcon in iso_conn_del(), to
avoid more complex reasoning on races about who holds the last
reference.

## References
- https://git.kernel.org/stable/c/aa9f7cb2bd3a2be998ceb739fc9a2f986eba43eb
- https://git.kernel.org/stable/c/cdce8af9291d8a1f8916c271de029bf558d9e8ec
- https://git.kernel.org/stable/c/e941799c31f68e67ce0976efb38a79101f921b64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80721.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80721
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
