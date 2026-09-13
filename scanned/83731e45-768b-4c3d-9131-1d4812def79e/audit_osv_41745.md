# [C] 9p: avoid putting oldfid in p9_client_walk() error path

## Summary
Severity: Critical
Advisory: CVE-2026-63795
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63795
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: avoid putting oldfid in p9_client_walk() error path

When p9_client_walk() is called with clone set to false, fid aliases
oldfid. If the walk subsequently fails after the request has been sent,
the error path jumps to clunk_fid, which currently calls p9_fid_put(fid)
unconditionally.

This drops a reference to oldfid even though ownership of oldfid remains
with the caller. If this is the last reference, oldfid can be clunked and
destroyed while the caller still expects it to be valid. A later use or
put of oldfid can then trigger a use-after-free or refcount underflow.

Fix this by only putting fid in the clunk_fid error path when it does not
alias oldfid, matching the existing guard in the error path below.

This can be triggered when a multi-component walk is split into multiple
p9_client_walk() calls and a later non-cloning walk fails. A reproducer
and refcount warning logs are available on request.

## References
- https://git.kernel.org/stable/c/1a3860d46e3eb47dbd60339783cdad7904486b9f
- https://git.kernel.org/stable/c/6dbe9443d9f5f7fb6d319a7b77108853ae6c6bea
- https://git.kernel.org/stable/c/99c379ca1e221c3d75c7c804ebbf4e5ee37a3070
- https://git.kernel.org/stable/c/a61bdcba4f64c2f90d01461913f429ab151f1ca6
- https://git.kernel.org/stable/c/a7656d368265d085ac9bb85ab31b0cdb72ad8c38
- https://git.kernel.org/stable/c/b84f46179c806450b89821221ea5bd9a1698aba8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63795.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63795
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
