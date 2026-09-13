# [M] vsock: prevent null-ptr-deref in vsock_*[has_data|has_space]

## Summary
Severity: Medium
Advisory: CVE-2025-21666
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21666
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: prevent null-ptr-deref in vsock_*[has_data|has_space]

Recent reports have shown how we sometimes call vsock_*_has_data()
when a vsock socket has been de-assigned from a transport (see attached
links), but we shouldn't.

Previous commits should have solved the real problems, but we may have
more in the future, so to avoid null-ptr-deref, we can return 0
(no space, no data available) but with a warning.

This way the code should continue to run in a nearly consistent state
and have a warning that allows us to debug future problems.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/91751e248256efc111e52e15115840c35d85abaf
- https://git.kernel.org/stable/c/9e5fed46ccd2c34c5fa5a9c8825ce4823fdc853e
- https://git.kernel.org/stable/c/b52e50dd4fabd12944172bd486a4f4853b7f74dd
- https://git.kernel.org/stable/c/bc9c49341f9728c31fe248c5fbba32d2e81a092b
- https://git.kernel.org/stable/c/c23d1d4f8efefb72258e9cedce29de10d057f8ca
- https://git.kernel.org/stable/c/daeac89cdb03d30028186f5ff7dc26ec8fa843e7
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21666.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21666
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
