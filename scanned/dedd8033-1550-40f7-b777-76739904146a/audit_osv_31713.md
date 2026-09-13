# [H] vsock/virtio: discard packets if the transport changes

## Summary
Severity: High
Advisory: CVE-2025-21669
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21669
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: discard packets if the transport changes

If the socket has been de-assigned or assigned to another transport,
we must discard any packets received because they are not expected
and would cause issues when we access vsk->transport.

A possible scenario is described by Hyunwoo Kim in the attached link,
where after a first connect() interrupted by a signal, and a second
connect() failed, we can find `vsk->transport` at NULL, leading to a
NULL pointer dereference.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/18a7fc371d1dbf8deff16c2dd9292bcc73f43040
- https://git.kernel.org/stable/c/2cb7c756f605ec02ffe562fb26828e4bcc5fdfc1
- https://git.kernel.org/stable/c/6486915fa661584d70e8e7e4068c6c075c67dd6d
- https://git.kernel.org/stable/c/677579b641af109613564460a4e3bdcb16850b61
- https://git.kernel.org/stable/c/88244163bc7e7b0ce9dd7bf4c8a563b41525c3ee
- https://git.kernel.org/stable/c/d88b249e14bd0ee1e46bbe4f456e22e01b8c68de
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21669.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
