# [C] RDMA/rtrs: Fix use-after-free in path file creation cleanup

## Summary
Severity: Critical
Advisory: CVE-2026-64033
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64033
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.209, >=5.16.0 <6.1.175, >=5.17.0 <6.6.142, >=6.2.0 <6.12.92, >=6.7.0 <6.18.34, >=6.13.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rtrs: Fix use-after-free in path file creation cleanup

In the error path of rtrs_srv_create_path_files(), the sysfs root folders
may already have been created and srv_path->kobj may already have been
initialized. If a later step fails, the cleanup currently calls
kobject_put(&srv_path->kobj) before
rtrs_srv_destroy_once_sysfs_root_folders(srv_path).

kobject_put() may drop the last reference to srv_path->kobj and invoke the
release callback, rtrs_srv_release(), which frees srv_path. The following
call to rtrs_srv_destroy_once_sysfs_root_folders(srv_path) then
dereferences srv_path internally to access srv_path->srv, resulting in a
use-after-free.

This failure path is reached before rtrs_srv_create_path_files() returns
success, so the successful-path lifetime handling is not involved.

Fix this by destroying the sysfs root folders before calling
kobject_put(&srv_path->kobj), so srv_path is still valid while the helper
accesses it.

This issue was found by a static analysis tool I am developing.

## References
- https://git.kernel.org/stable/c/00904a73272b9f3ef3952fe69a833909dccad1ef
- https://git.kernel.org/stable/c/01e42aabaf7632beb4bf235c7238b96c746d4144
- https://git.kernel.org/stable/c/548f3956e53a7f7bde912d8129010b8986d5e602
- https://git.kernel.org/stable/c/5b74373390113fba798a76b483837029ab010fef
- https://git.kernel.org/stable/c/92060ab1c5115674cf319175550f85f68405121f
- https://git.kernel.org/stable/c/b0e9706fb2859064bb6c677554c4d20c713aa8e0
- https://git.kernel.org/stable/c/eae62c5451e67e8b033c1681fd3b85d7e9a9a28f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64033.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64033
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
