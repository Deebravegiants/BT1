# [H] ASoC: meson: aiu: Validate written enum values

## Summary
Severity: High
Advisory: CVE-2026-74294
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74294
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: meson: aiu: Validate written enum values

The AIU HDMI and internal codec mux put callbacks use the written enum
value with snd_soc_enum_item_to_val() before checking whether the value is
valid for the enumeration.

Reject out-of-range values before converting the enum item, matching the
validation already done by the G12A HDMI and internal codec mux controls.

## References
- https://git.kernel.org/stable/c/0965892cc486ca554d72eeb62d85ccf8d0137a5a
- https://git.kernel.org/stable/c/d65adf85477247be04ac86886f8edfaa047b5d4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74294.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
