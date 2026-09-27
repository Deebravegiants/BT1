# [M] media: meson: vdec: fix possible refcount leak in vdec_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49887
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49887
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: meson: vdec: fix possible refcount leak in vdec_probe()

v4l2_device_unregister need to be called to put the refcount got by
v4l2_device_register when vdec_probe fails or vdec_remove is called.

## References
- https://git.kernel.org/stable/c/0457e7b12ece1a7e41fa0ae8b7e47c0a72a83bef
- https://git.kernel.org/stable/c/70119756311a0be3b95bec2e1ba714673e90feba
- https://git.kernel.org/stable/c/7718999356234d9cc6a11b4641bb773928f1390f
- https://git.kernel.org/stable/c/be6e22f54623d8a856a4f167b25be73c2ff1ff80
- https://git.kernel.org/stable/c/f96ad391d054bd5c36994f98afd6a12cbb5600bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49887.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
