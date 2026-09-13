# [M] virtio_pmem: Check device status before requesting flush

## Summary
Severity: Medium
Advisory: CVE-2024-50184
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50184
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio_pmem: Check device status before requesting flush

If a pmem device is in a bad status, the driver side could wait for
host ack forever in virtio_pmem_flush(), causing the system to hang.

So add a status check in the beginning of virtio_pmem_flush() to return
early if the device is not activated.

## References
- https://git.kernel.org/stable/c/4ce662fe4be6fbc2595d9ef4888b2b6e778c99ed
- https://git.kernel.org/stable/c/59ac565c6277d4be6661e81ea6a7f3ca2c5e4e36
- https://git.kernel.org/stable/c/6a5ca0ab94e13a1474bf7ad8437a975c2193618f
- https://git.kernel.org/stable/c/9a2bc9b6f929a2ce1ebe4d1a796ddab37568c5b4
- https://git.kernel.org/stable/c/b01793cc63dd39c8f12b9a3d8dc115fbebb19e2a
- https://git.kernel.org/stable/c/ce7a3a62cc533c922072f328fd2ea2fd7cb893d4
- https://git.kernel.org/stable/c/e25fbcd97cf52c3c9824d44b5c56c19673c3dd50
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50184.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
