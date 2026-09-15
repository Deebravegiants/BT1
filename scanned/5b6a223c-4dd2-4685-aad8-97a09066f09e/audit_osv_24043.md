# [M] mISDN: fix possible memory leak in mISDN_register_device()

## Summary
Severity: Medium
Advisory: CVE-2022-49915
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49915
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mISDN: fix possible memory leak in mISDN_register_device()

Afer commit 1fa5ae857bb1 ("driver core: get rid of struct device's
bus_id string array"), the name of device is allocated dynamically,
add put_device() to give up the reference, so that the name can be
freed in kobject_cleanup() when the refcount is 0.

Set device class before put_device() to avoid null release() function
WARN message in device_release().

## References
- https://git.kernel.org/stable/c/029d5b7688a2f3a86f2a3be5a6ba9cc968c80e41
- https://git.kernel.org/stable/c/080aabfb29b2ee9cbb8894a1d039651943d3773e
- https://git.kernel.org/stable/c/0d4e91efcaee081e919b3c50e875ecbb84290e41
- https://git.kernel.org/stable/c/2ff6b669523d3b3d253a044fa9636a67d0694995
- https://git.kernel.org/stable/c/a636fc5a7cabd05699b5692ad838c2c7a3abec7b
- https://git.kernel.org/stable/c/d1d1aede313eb2b9a84afd60ff6cfb7c33631e0e
- https://git.kernel.org/stable/c/e77d213843e67b4373285712699b692f9c743f61
- https://git.kernel.org/stable/c/e7d1d4d9ac0dfa40be4c2c8abd0731659869b297
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49915.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49915
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
