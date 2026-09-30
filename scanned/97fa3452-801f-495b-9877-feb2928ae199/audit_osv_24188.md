# [M] ASoC: mediatek: mt8183: fix refcount leak in mt8183_mt6358_ts3a227_max98357_dev_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-50392
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50392
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mediatek: mt8183: fix refcount leak in mt8183_mt6358_ts3a227_max98357_dev_probe()

The node returned by of_parse_phandle() with refcount incremented,
of_node_put() needs be called when finish using it. So add it in the
error path in mt8183_mt6358_ts3a227_max98357_dev_probe().

## References
- https://git.kernel.org/stable/c/156b0c19c1a44153e34cfdfa5937546a93dcb288
- https://git.kernel.org/stable/c/38eef3be38ab895959c442702864212cc3beb96c
- https://git.kernel.org/stable/c/574bd4d14a9297a1c69ad41001caf00fdd17d305
- https://git.kernel.org/stable/c/82f7c814edda353b4781f356d3ab90e943d5eac4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50392.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
