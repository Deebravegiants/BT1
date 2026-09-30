# [H] net/mlx5e: xsk: Fix crash on regular rq reactivation

## Summary
Severity: High
Advisory: CVE-2023-53394
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53394
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: xsk: Fix crash on regular rq reactivation

When the regular rq is reactivated after the XSK socket is closed
it could be reading stale cqes which eventually corrupts the rq.
This leads to no more traffic being received on the regular rq and a
crash on the next close or deactivation of the rq.

Kal Cuttler Conely reported this issue as a crash on the release
path when the xdpsock sample program is stopped (killed) and restarted
in sequence while traffic is running.

This patch flushes all cqes when during the rq flush. The cqe flushing
is done in the reset state of the rq. mlx5e_rq_to_ready code is moved
into the flush function to allow for this.

## References
- https://git.kernel.org/stable/c/02a84eb2af6bea7871cd34264fb27f141f005fd9
- https://git.kernel.org/stable/c/39646d9bcd1a65d2396328026626859a1dab59d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53394.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53394
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
