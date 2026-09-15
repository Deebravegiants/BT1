# [H] vdpa/mlx5: add validation for VIRTIO_NET_CTRL_MQ_VQ_PAIRS_SET command

## Summary
Severity: High
Advisory: CVE-2022-48864
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48864
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.29, >=5.16.0 <5.16.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

vdpa/mlx5: add validation for VIRTIO_NET_CTRL_MQ_VQ_PAIRS_SET command

When control vq receives a VIRTIO_NET_CTRL_MQ_VQ_PAIRS_SET command
request from the driver, presently there is no validation against the
number of queue pairs to configure, or even if multiqueue had been
negotiated or not is unverified. This may lead to kernel panic due to
uninitialized resource for the queues were there any bogus request
sent down by untrusted driver. Tie up the loose ends there.

## References
- https://git.kernel.org/stable/c/9f6effca75626c7a7c7620dabcb1a254ca530230
- https://git.kernel.org/stable/c/e7e118416465f2ba8b55007e5b789823e101421e
- https://git.kernel.org/stable/c/ed0f849fc3a63ed2ddf5e72cdb1de3bdbbb0f8eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48864.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
