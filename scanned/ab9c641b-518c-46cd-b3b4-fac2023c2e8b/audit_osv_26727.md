# [H] xsk: fix refcount underflow in error path

## Summary
Severity: High
Advisory: CVE-2023-53698
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53698
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.127, >=5.16.0 <6.1.46, >=5.18.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: fix refcount underflow in error path

Fix a refcount underflow problem reported by syzbot that can happen
when a system is running out of memory. If xp_alloc_tx_descs() fails,
and it can only fail due to not having enough memory, then the error
path is triggered. In this error path, the refcount of the pool is
decremented as it has incremented before. However, the reference to
the pool in the socket was not nulled. This means that when the socket
is closed later, the socket teardown logic will think that there is a
pool attached to the socket and try to decrease the refcount again,
leading to a refcount underflow.

I chose this fix as it involved adding just a single line. Another
option would have been to move xp_get_pool() and the assignment of
xs->pool to after the if-statement and using xs_umem->pool instead of
xs->pool in the whole if-statement resulting in somewhat simpler code,
but this would have led to much more churn in the code base perhaps
making it harder to backport.

## References
- https://git.kernel.org/stable/c/15b453cf7348973217558235b9ece2ee5fea6777
- https://git.kernel.org/stable/c/3e7722c31d4167eb7f3ffd35aba52cab69b79072
- https://git.kernel.org/stable/c/789fcd94c9cac133dd4d96e193188661aca9f6c3
- https://git.kernel.org/stable/c/85c2c79a07302fe68a1ad5cc449458cc559e314d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53698.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53698
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
