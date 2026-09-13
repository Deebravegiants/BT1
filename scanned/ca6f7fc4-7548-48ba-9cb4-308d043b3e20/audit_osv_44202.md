# [H] ASoC: codecs: lpass-tx-macro: Fix enum kcontrol accesses

## Summary
Severity: High
Advisory: CVE-2026-80583
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80583
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.47, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: lpass-tx-macro: Fix enum kcontrol accesses

The "DEC0 MODE" to "DEC7 MODE" controls are enumerated, but
tx_macro_dec_mode_get() and tx_macro_dec_mode_put() access their
value through ucontrol->value.integer.value[0] (a long) instead of
ucontrol->value.enumerated.item[0] (an unsigned int).

This same pattern was fixed in the sibling drivers by
commit bcfe5f76cc40 ("ASoC: codecs: rx-macro: fix accessing array
out of bounds for enum type") and
commit 0ea5eff7c606 ("ASoC: codecs: va-macro: fix accessing array
out of bounds for enum type"), but tx-macro was missed.

On 64-bit kernels built with CONFIG_SND_CTL_DEBUG, the elem value
sanity check catches the 4 bytes written past the enumerated item
and every read of these controls fails with -EINVAL:

  snd-sm8250 sound: control 2:0:0:DEC0 MODE:0: access overflow

## References
- https://git.kernel.org/stable/c/1ba381759e45d5d0442452cfa5c42e836191a568
- https://git.kernel.org/stable/c/2ed3601e9db08fbdb071bd3d7bd8f115d6d871b0
- https://git.kernel.org/stable/c/3ee3c26ceee562079596abc9bc3307dd56dab4ed
- https://git.kernel.org/stable/c/48b76879f5bfc8584b99052510ac645c6ade8d2b
- https://git.kernel.org/stable/c/b6baab796d11fb84c0e9444ffca91af5eab22c25
- https://git.kernel.org/stable/c/dbc81b518f6936131bfd858be71cd4295136809c
- https://git.kernel.org/stable/c/f84f2c81d792cf1e65571108a3bdd2c29e09e995
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80583.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80583
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
