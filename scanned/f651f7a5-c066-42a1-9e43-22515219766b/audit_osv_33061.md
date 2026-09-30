# [H] ASoC: mediatek: mt8365-dai-i2s: pass correct size to mt8365_dai_set_priv

## Summary
Severity: High
Advisory: CVE-2025-38662
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38662
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.41, >=6.13.0 <6.15.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mediatek: mt8365-dai-i2s: pass correct size to mt8365_dai_set_priv

Given mt8365_dai_set_priv allocate priv_size space to copy priv_data which
means we should pass mt8365_i2s_priv[i] or "struct mtk_afe_i2s_priv"
instead of afe_priv which has the size of "struct mt8365_afe_private".

Otherwise the KASAN complains about.

[   59.389765] BUG: KASAN: global-out-of-bounds in mt8365_dai_set_priv+0xc8/0x168 [snd_soc_mt8365_pcm]
...
[   59.394789] Call trace:
[   59.395167]  dump_backtrace+0xa0/0x128
[   59.395733]  show_stack+0x20/0x38
[   59.396238]  dump_stack_lvl+0xe8/0x148
[   59.396806]  print_report+0x37c/0x5e0
[   59.397358]  kasan_report+0xac/0xf8
[   59.397885]  kasan_check_range+0xe8/0x190
[   59.398485]  asan_memcpy+0x3c/0x98
[   59.399022]  mt8365_dai_set_priv+0xc8/0x168 [snd_soc_mt8365_pcm]
[   59.399928]  mt8365_dai_i2s_register+0x1e8/0x2b0 [snd_soc_mt8365_pcm]
[   59.400893]  mt8365_afe_pcm_dev_probe+0x4d0/0xdf0 [snd_soc_mt8365_pcm]
[   59.401873]  platform_probe+0xcc/0x228
[   59.402442]  really_probe+0x340/0x9e8
[   59.402992]  driver_probe_device+0x16c/0x3f8
[   59.403638]  driver_probe_device+0x64/0x1d8
[   59.404256]  driver_attach+0x1dc/0x4c8
[   59.404840]  bus_for_each_dev+0x100/0x190
[   59.405442]  driver_attach+0x44/0x68
[   59.405980]  bus_add_driver+0x23c/0x500
[   59.406550]  driver_register+0xf8/0x3d0
[   59.407122]  platform_driver_register+0x68/0x98
[   59.407810]  mt8365_afe_pcm_driver_init+0x2c/0xff8 [snd_soc_mt8365_pcm]

## References
- https://git.kernel.org/stable/c/1dc0ed16cfbc3c28a07a89904071cfa802fdcee1
- https://git.kernel.org/stable/c/6bea85979d05470e6416a2bb504a9bcd9178304c
- https://git.kernel.org/stable/c/6e621dd99c57db916842865debaa65f20bbd6d8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38662.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
