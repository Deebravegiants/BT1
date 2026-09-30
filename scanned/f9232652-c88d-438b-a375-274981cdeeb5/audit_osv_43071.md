# [H] ASoC: SDCA: Validate written enum value in ge_put_enum_double()

## Summary
Severity: High
Advisory: CVE-2026-72415
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72415
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SDCA: Validate written enum value in ge_put_enum_double()

ge_put_enum_double() passes the user-supplied enumeration index
item[0] to snd_soc_enum_item_to_val() without checking it against the
number of items in the enum:

	ret = snd_soc_enum_item_to_val(e, item[0]);

snd_soc_enum_item_to_val() indexes the heap-allocated e->values[] array
with that index (e->values is set from a devm_kcalloc() of e->items
entries), so a control write with an out-of-range item[0] reads past the
end of the values buffer.  The bounds check in
snd_soc_dapm_put_enum_double() only runs afterwards, so it does not
prevent the read here.

Reject an out-of-range item before using it, matching the other enum put
handlers.

This issue was pointed out by the Sashiko AI review bot while reviewing a
related enum-validation series:
https://lore.kernel.org/all/20260609125735.CEB651F00893@smtp.kernel.org/

## References
- https://git.kernel.org/stable/c/1ce42a11bed134903e352010a01fa53073a6b395
- https://git.kernel.org/stable/c/33387bf9bb6116a0429f823f8dab3accf8f8e09c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72415.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72415
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
