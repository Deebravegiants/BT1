# [H] CVE-2021-32846

## Summary
Severity: High
Advisory: CVE-2021-32846
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2021-32846
Type: osv

## Details
HyperKit is a toolkit for embedding hypervisor capabilities in an application. In versions 0.20210107, function `pci_vtsock_proc_tx` in `virtio-sock` can lead to to uninitialized memory use. In this situation, there is a check for the return value to be less or equal to `VTSOCK_MAXSEGS`, but that check is not sufficient because the function can return `-1` if it finds an error it cannot recover from. Moreover, the negative return value will be used by `iovec_pull` in a while condition that can further lead to more corruption because the function is not designed to handle a negative `iov_len`. This issue may lead to a guest crashing the host causing a denial of service and, under certain circumstance, memory corruption. This issue is fixed in commit af5eba2360a7351c08dfd9767d9be863a50ebaba.

## References
- https://securitylab.github.com/advisories/GHSL-2021-054_057-moby-hyperkit/
- https://github.com/moby/hyperkit/commit/af5eba2360a7351c08dfd9767d9be863a50ebaba
- https://github.com/moby/hyperkit/pull/313
