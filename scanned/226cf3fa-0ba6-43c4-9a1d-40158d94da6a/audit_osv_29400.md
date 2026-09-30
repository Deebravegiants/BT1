# [H] nvme-pci: add missing condition check for existence of mapped data

## Summary
Severity: High
Advisory: CVE-2024-42276
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42276
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: add missing condition check for existence of mapped data

nvme_map_data() is called when request has physical segments, hence
the nvme_unmap_data() should have same condition to avoid dereference.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3f8ec1d6b0ebd8268307d52be8301973fa5a01ec
- https://git.kernel.org/stable/c/70100fe721840bf6d8e5abd25b8bffe4d2e049b7
- https://git.kernel.org/stable/c/77848b379e9f85a08048a2c8b3b4a7e8396f5f83
- https://git.kernel.org/stable/c/7cc1f4cd90a00b6191cb8cda2d1302fdce59361c
- https://git.kernel.org/stable/c/be23ae63080e0bf9e246ab20207200bca6585eba
- https://git.kernel.org/stable/c/c31fad1470389666ac7169fe43aa65bf5b7e2cfd
- https://git.kernel.org/stable/c/d135c3352f7c947a922da93c8e763ee6bc208b64
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42276.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
