# [M] nfc: nfcmrvl: Fix potential memory leak in nfcmrvl_i2c_nci_send()

## Summary
Severity: Medium
Advisory: CVE-2022-49922
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49922
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: nfcmrvl: Fix potential memory leak in nfcmrvl_i2c_nci_send()

nfcmrvl_i2c_nci_send() will be called by nfcmrvl_nci_send(), and skb
should be freed in nfcmrvl_i2c_nci_send(). However, nfcmrvl_nci_send()
will only free skb when i2c_master_send() return >=0, which means skb
will memleak when i2c_master_send() failed. Free skb no matter whether
i2c_master_send() succeeds.

## References
- https://git.kernel.org/stable/c/52438e734c1566f5e2bcd9a065d2d65e306c0555
- https://git.kernel.org/stable/c/5dfdac5e3f8db5f4445228c44f64091045644a3b
- https://git.kernel.org/stable/c/825656ae61e73ddc05f585e6258d284c87064b10
- https://git.kernel.org/stable/c/92a1df9c6da20c02cf9872f8b025a66ddb307aeb
- https://git.kernel.org/stable/c/93d904a734a74c54d945a9884b4962977f1176cd
- https://git.kernel.org/stable/c/c8e7d4a1166f063703955f1b2e765a6db5bf1771
- https://git.kernel.org/stable/c/dd0ee55ead91fbb16889dbe7ff0b0f7c9e4e849d
- https://git.kernel.org/stable/c/f30060efcf18883748a0541aa41acef183cd9c0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49922.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
