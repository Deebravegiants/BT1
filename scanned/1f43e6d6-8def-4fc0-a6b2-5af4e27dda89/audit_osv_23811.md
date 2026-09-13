# [M] ASoC: mediatek: Fix missing of_node_put in mt2701_wm8960_machine_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49517
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49517
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mediatek: Fix missing of_node_put in mt2701_wm8960_machine_probe

This node pointer is returned by of_parse_phandle() with
refcount incremented in this function.
Calling of_node_put() to avoid the refcount leak.

## References
- https://git.kernel.org/stable/c/05654431a18fe24e5e46a375d98904134628a102
- https://git.kernel.org/stable/c/318afb1442eeef089fe7f8a8297d97c0302ff6f6
- https://git.kernel.org/stable/c/61a85a20e8df5e0a92cfe169c92425c7bae0753b
- https://git.kernel.org/stable/c/9345122f5fb9f97a206f440f38bb656e53f46912
- https://git.kernel.org/stable/c/94587aa17abf8b26f543d2b29c44abc21bc36836
- https://git.kernel.org/stable/c/bc2afecaabd2a2c9f17e43b4793a30e3461bfb29
- https://git.kernel.org/stable/c/c71494f5f2b444adfd992a7359a0d2a791642b39
- https://git.kernel.org/stable/c/f279c49f17ce10866087ea6c0c57382158974b63
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49517.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49517
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
