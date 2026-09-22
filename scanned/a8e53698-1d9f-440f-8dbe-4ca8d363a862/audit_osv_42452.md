# [H] sctp: avoid auth_enable sysctl UAF during netns teardown

## Summary
Severity: High
Advisory: CVE-2026-68162
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68162
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.292, >=5.5.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.151, >=6.7.0 <6.12.101, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: avoid auth_enable sysctl UAF during netns teardown

proc_sctp_do_auth() updates the SCTP control socket after changing
net.sctp.auth_enable. The handler gets the per-net SCTP state from
ctl->data, so an already opened sysctl file can still target a network
namespace while that namespace is being torn down.

SCTP previously registered its per-net sysctls from sctp_defaults_init(),
while the control socket is created later from sctp_ctrlsock_init(). This
exposed a window during initialization where auth_enable was writable
before net->sctp.ctl_sock existed, and a teardown window where auth_enable
stayed writable after inet_ctl_sock_destroy() had released the control
socket.

Move the per-net SCTP sysctl registration into sctp_ctrlsock_init() after
sctp_ctl_sock_init() succeeds, and unregister the sysctl table before
destroying the control socket in sctp_ctrlsock_exit(). If sysctl
registration fails after the control socket was created, destroy the
control socket in the same init path.

Make sctp_sysctl_net_unregister() tolerate a missing header and clear the
saved pointer so init-error and exit paths can safely share the unregister
helper.

## References
- https://git.kernel.org/stable/c/158f3cc332dc53f43ec20060233d7c3cecd6d912
- https://git.kernel.org/stable/c/19573dcddb8819fd68d6cd1f916c1c99c3fa4ff4
- https://git.kernel.org/stable/c/626bda8cfe43dff19a9833ff6ba055a817b5455c
- https://git.kernel.org/stable/c/66700c0719675e0e118ae83b2d7168dacd69dd3d
- https://git.kernel.org/stable/c/a50e73488e0bbdd262b3be3c9a1d8dd078382381
- https://git.kernel.org/stable/c/be6aae9d1b91c603adb35872d37d40e83daf8758
- https://git.kernel.org/stable/c/ceb7190b5c873d4a1267a1600c5aa52c600e929f
- https://git.kernel.org/stable/c/f8d5e7846025f4ab15a461235f8ebae9094a361a
- https://git.kernel.org/stable/c/fd66854a22661929245f3d2b244c432bc8b1a150
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68162.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
