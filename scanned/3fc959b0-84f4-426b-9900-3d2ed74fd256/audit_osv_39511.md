# [H] libceph: Prevent potential null-ptr-deref in ceph_handle_auth_reply()

## Summary
Severity: High
Advisory: CVE-2026-46024
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46024
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Prevent potential null-ptr-deref in ceph_handle_auth_reply()

If a message of type CEPH_MSG_AUTH_REPLY contains a zero value for both
protocol and result, this is currently not treated as an error. In case
of ac->negotiating == true and ac->protocol > 0, this leads to setting
ac->protocol = 0 and ac->ops = NULL. Thereafter, the check for
ac->protocol != protocol returns false, and init_protocol() is not
called. Subsequently, ac->ops->handle_reply() is called, which leads to
a null pointer dereference, because ac->ops is still NULL.

This patch changes the check for ac->protocol != protocol to
!ac->protocol, as this also includes the case when the protocol was set
to zero in the message. This causes the message to be treated as
containing a bad auth protocol.

## References
- https://git.kernel.org/stable/c/016bc663657366d386993f63eb31072eb45a2b77
- https://git.kernel.org/stable/c/4b2738b93edad661178340239de657d876b73d3d
- https://git.kernel.org/stable/c/5199c125d25aeae8615c4fc31652cc0fe624338e
- https://git.kernel.org/stable/c/8f2be7285941a33a9f72579a23b96392f83c758e
- https://git.kernel.org/stable/c/927e4bd5692f2a4901808822981fb2c8d4456548
- https://git.kernel.org/stable/c/9ded62c302c0342efdb5eda3bf6e75720caad0df
- https://git.kernel.org/stable/c/f101271fcf55d7eacfefd610b51ec65f46ba8118
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46024.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
