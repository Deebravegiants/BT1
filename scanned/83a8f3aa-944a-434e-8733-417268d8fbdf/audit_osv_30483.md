# [H] media: mgb4: protect driver against spectre

## Summary
Severity: High
Advisory: CVE-2024-53062
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53062
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mgb4: protect driver against spectre

Frequency range is set from sysfs via frequency_range_store(),
being vulnerable to spectre, as reported by smatch:

	drivers/media/pci/mgb4/mgb4_cmt.c:231 mgb4_cmt_set_vin_freq_range() warn: potential spectre issue 'cmt_vals_in' [r]
	drivers/media/pci/mgb4/mgb4_cmt.c:238 mgb4_cmt_set_vin_freq_range() warn: possible spectre second half.  'reg_set'

Fix it.

## References
- https://git.kernel.org/stable/c/2aee207e5b3c94ef859316008119ea06d6798d49
- https://git.kernel.org/stable/c/e0bc90742bbd6eb9c63e6c22f8f6e10be7b1e225
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
