# [H] ASoC: fsl: fsl_audmix: Validate written enum values

## Summary
Severity: High
Advisory: CVE-2026-74293
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74293
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: fsl: fsl_audmix: Validate written enum values

fsl_audmix_put_mix_clk_src() and fsl_audmix_put_out_src()
convert the user-provided enum item with snd_soc_enum_item_to_val()
before checking whether the item is within the enum's item count.

The generic snd_soc_put_enum_double() helper performs that
validation, but these callbacks use the converted value first: the
clock-source path tests it with BIT(), and the output-source path
indexes the prms transition table with it.

Reject out-of-range enum items before converting them.

## References
- https://git.kernel.org/stable/c/0b10c6203e62d9e7337cc401568b201f9bac79ec
- https://git.kernel.org/stable/c/0f1510e84d7bfc3eb9538efa65c6ea0aadf1078c
- https://git.kernel.org/stable/c/3cd17e4e2871114d5579fa7bc8da66faf7fc1930
- https://git.kernel.org/stable/c/5b7a23c1ed04e794ef3b31e452ef5c93e1e34b4a
- https://git.kernel.org/stable/c/7513831b90a38d55fa089e3e1b49691e467afee6
- https://git.kernel.org/stable/c/8fb4364eb494b926d009bfaf3c98f07c3aa5d9f3
- https://git.kernel.org/stable/c/b36d6d48faa6b1bb723b8f4e527c531a1a68520e
- https://git.kernel.org/stable/c/b4774a7da12b14fc37219ab4368d1907f9b5aca4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74293.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74293
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
