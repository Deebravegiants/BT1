# [M] nfc: nxp-nci: Fix potential memory leak in nxp_nci_send()

## Summary
Severity: Medium
Advisory: CVE-2022-49923
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49923
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: nxp-nci: Fix potential memory leak in nxp_nci_send()

nxp_nci_send() will call nxp_nci_i2c_write(), and only free skb when
nxp_nci_i2c_write() failed. However, even if the nxp_nci_i2c_write()
run succeeds, the skb will not be freed in nxp_nci_i2c_write(). As the
result, the skb will memleak. nxp_nci_send() should also free the skb
when nxp_nci_i2c_write() succeeds.

## References
- https://git.kernel.org/stable/c/3cba1f061bfe23fece2841129ca2862cdec29d5c
- https://git.kernel.org/stable/c/3ecf0f4227029b2c42e036b10ff6e5d09e20821e
- https://git.kernel.org/stable/c/7bf1ed6aff0f70434bd0cdd45495e83f1dffb551
- https://git.kernel.org/stable/c/9ae2c9a91ff068f4c3e392f47e8e26a1c9f85ebb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49923.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
