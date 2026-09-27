# [H] apparmor: fix race in unix socket mediation when peer_path is used

## Summary
Severity: High
Advisory: CVE-2026-72462
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72462
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix race in unix socket mediation when peer_path is used

The holding a reference to the peer_sk is not enough to ensure access
to the peer sk path. Accessing the path outside of the state lock
allows for a race with unix_release_sock(). Fix this by taking the
state lock and getting a reference to the path under lock.

Ideally for connected sockets we would cache this information so we
don't have to take the lock here. But for now just fix the race.

## References
- https://git.kernel.org/stable/c/b1aea2c1960771a276d7e68c7424168eccd0c3da
- https://git.kernel.org/stable/c/d680472db98823d90fc91362910901e468269318
- https://git.kernel.org/stable/c/d8ea44f6090c087fe255d9512fb808574b4d88e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72462.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72462
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
