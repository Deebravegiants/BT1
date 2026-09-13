# [H] NFSv4: include MAY_WRITE in open permission mask for O_TRUNC

## Summary
Severity: High
Advisory: CVE-2026-64298
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64298
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4: include MAY_WRITE in open permission mask for O_TRUNC

POSIX requires write permission to truncate a file, so an open() that
specifies O_TRUNC must be authorized for write access regardless of the
O_ACCMODE access mode.

nfs_open_permission_mask() builds the access mask passed to
nfs_may_open(), which is the local authorization gate for OPENs the
client serves itself from a cached write delegation via the
can_open_delegated() path in nfs4_try_open_cached().  The mask is
derived from O_ACCMODE alone, so an open(O_RDONLY | O_TRUNC) against a
file the caller cannot write requests only MAY_READ and passes the
local check.  The OPEN is then satisfied locally and the truncation is
issued to the server as a SETATTR(size=0) over the delegation stateid,
which the server accepts under standard write-delegation semantics.
POSIX requires that this open fail with EACCES.

Include MAY_WRITE in the mask whenever O_TRUNC is set so the local
check matches the access the server would have enforced.

## References
- https://git.kernel.org/stable/c/22c1fd1355ad4ca27aa7f0fa02719122dd92d9de
- https://git.kernel.org/stable/c/30fdf4df6c3c00efec947e4ddf97f0fdd4473628
- https://git.kernel.org/stable/c/4817c8974315b666e895b7d1bb83cd3664c323b1
- https://git.kernel.org/stable/c/5140f099ecd8a2f2808b7f7b720ee1bad8468974
- https://git.kernel.org/stable/c/6bd7d0a06b53c4e797e1a9cea0d2d41aa1b26230
- https://git.kernel.org/stable/c/a937e92c1d00534b5c2e3e9f4381b7e988180797
- https://git.kernel.org/stable/c/cb148a2762d644bff1894728e8835a9a4b84f9ea
- https://git.kernel.org/stable/c/e36501b7d4abdcd6d69a7cb901b2f286b7a3d041
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64298.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64298
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
