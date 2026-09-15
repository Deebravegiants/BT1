# [H] libceph: return the handler error from mon_handle_auth_done()

## Summary
Severity: High
Advisory: CVE-2026-22992
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-22992
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.198, >=5.16.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: return the handler error from mon_handle_auth_done()

Currently any error from ceph_auth_handle_reply_done() is propagated
via finish_auth() but isn't returned from mon_handle_auth_done().  This
results in higher layers learning that (despite the monitor considering
us to be successfully authenticated) something went wrong in the
authentication phase and reacting accordingly, but msgr2 still trying
to proceed with establishing the session in the background.  In the
case of secure mode this can trigger a WARN in setup_crypto() and later
lead to a NULL pointer dereference inside of prepare_auth_signature().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/33908769248b38a5e77cf9292817bb28e641992d
- https://git.kernel.org/stable/c/77229551f2cf72f3e35636db68e6a825b912cf16
- https://git.kernel.org/stable/c/9e0101e57534ef0e7578dd09608a6106736b82e5
- https://git.kernel.org/stable/c/d2c4a5f6996683f287f3851ef5412797042de7f1
- https://git.kernel.org/stable/c/e097cd858196b1914309e7e3d79b4fa79383754d
- https://git.kernel.org/stable/c/e84b48d31b5008932c0a0902982809fbaa1d3b70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22992.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22992
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
