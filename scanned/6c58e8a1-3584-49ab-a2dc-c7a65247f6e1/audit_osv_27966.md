# [M] Bluetooth: hci_core: Fix possible buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2024-26889
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26889
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.6.23, >=6.6.0 <6.7.11, >=6.7.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_core: Fix possible buffer overflow

struct hci_dev_info has a fixed size name[8] field so in the event that
hdev->name is bigger than that strcpy would attempt to write past its
size, so this fixes this problem by switching to use strscpy.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2e845867b4e279eff0a19ade253390470e07e8a1
- https://git.kernel.org/stable/c/2edce8e9a99dd5e4404259d52e754fdc97fb42c2
- https://git.kernel.org/stable/c/54a03e4ac1a41edf8a5087bd59f8241b0de96d3d
- https://git.kernel.org/stable/c/68644bf5ec6baaff40fc39b3529c874bfda709bd
- https://git.kernel.org/stable/c/6d5a9d4a7bcbb7534ce45a18a52e7bd23e69d8ac
- https://git.kernel.org/stable/c/81137162bfaa7278785b24c1fd2e9e74f082e8e4
- https://git.kernel.org/stable/c/8c28598a2c29201d2ba7fc37539a7d41c264fb10
- https://git.kernel.org/stable/c/a41c8efe659caed0e21422876bbb6b73c15b5244
- https://git.kernel.org/stable/c/d47e6c1932cee02954ea588c9f09fd5ecefeadfc
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26889.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
