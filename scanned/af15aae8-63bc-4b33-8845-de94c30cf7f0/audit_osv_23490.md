# [H] net: hisilicon: Fix potential use-after-free in hix5hd2_rx()

## Summary
Severity: High
Advisory: CVE-2022-48960
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48960
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <4.9.336, >=4.10.0 <4.14.302, >=4.15.0 <4.19.269, >=4.20.0 <5.4.227, >=5.5.0 <5.10.159, >=5.11.0 <5.15.83, >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hisilicon: Fix potential use-after-free in hix5hd2_rx()

The skb is delivered to napi_gro_receive() which may free it, after
calling this, dereferencing skb may trigger use-after-free.

## References
- https://git.kernel.org/stable/c/179499e7a240b2ef590f05eb379c810c26bbc8a4
- https://git.kernel.org/stable/c/1b6360a093ab8969c91a30bb58b753282e2ced4c
- https://git.kernel.org/stable/c/3a4eddd1cb023a71df4152fcc76092953e6fe95a
- https://git.kernel.org/stable/c/433c07a13f59856e4585e89e86b7d4cc59348fab
- https://git.kernel.org/stable/c/8067cd244cea2c332f8326842fd10158fa2cb64f
- https://git.kernel.org/stable/c/93aaa4bb72e388f6a4887541fd3d18b84f1b5ddc
- https://git.kernel.org/stable/c/b6307f7a2fc1c5407b6176f2af34a95214a8c262
- https://git.kernel.org/stable/c/b8ce0e6f9f88a6bb49d291498377e61ea27a5387
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48960.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48960
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
