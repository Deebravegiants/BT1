# [H] CVE-2021-32845

## Summary
Severity: High
Advisory: CVE-2021-32845
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2021-32845
Type: osv

## Details
HyperKit is a toolkit for embedding hypervisor capabilities in an application. In versions 0.20210107 and prior of HyperKit, the implementation of `qnotify` at `pci_vtrnd_notify` fails to check the return value of `vq_getchain`. This leads to `struct iovec iov;` being uninitialized and used to read memory in `len = (int) read(sc->vrsc_fd, iov.iov_base, iov.iov_len);` when an attacker is able to make `vq_getchain` fail. This issue may lead to a guest crashing the host causing a denial of service and, under certain circumstance, memory corruption. This issue is fixed in commit 41272a980197917df8e58ff90642d14dec8fe948.

## References
- https://securitylab.github.com/advisories/GHSL-2021-054_057-moby-hyperkit/
- https://github.com/moby/hyperkit/commit/41272a980197917df8e58ff90642d14dec8fe948
- https://github.com/moby/hyperkit/pull/313
