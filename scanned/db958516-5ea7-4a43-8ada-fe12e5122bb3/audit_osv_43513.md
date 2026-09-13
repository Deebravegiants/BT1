# [H] ASoC: codecs: hdac_hdmi: Validate written enum value

## Summary
Severity: High
Advisory: CVE-2026-74295
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74295
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: hdac_hdmi: Validate written enum value

hdac_hdmi_set_pin_port_mux() uses the written enum value to index the
texts array before calling snd_soc_dapm_put_enum_double(), which validates
that the value is within the enum item range.

An out-of-range value can therefore make the driver read past the texts
array before the helper rejects the write. Move the lookup after the helper
has accepted the value.

## References
- https://git.kernel.org/stable/c/0b08baeccdcf52fad328ad645f5b4fbee04eea34
- https://git.kernel.org/stable/c/216336418c007c4b44c650acf2fd3d2de5bb81e8
- https://git.kernel.org/stable/c/7f02e9064b6f84e7f93c72f134306271eb4f7de4
- https://git.kernel.org/stable/c/8cbf24714d6b3f553fc959632c9781176a73a9a7
- https://git.kernel.org/stable/c/9131e4b023e0db5764680034bdc94aeae0b0f33d
- https://git.kernel.org/stable/c/bc464a6a9e352daa17b1636c090cf3185710b9a0
- https://git.kernel.org/stable/c/d8961b5c7889b6ecc00f1409d36826df1665df27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74295.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74295
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
