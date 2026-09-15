# [H] ALSA: hda: tas2781: Fix wrong reference of tasdevice_priv

## Summary
Severity: High
Advisory: CVE-2025-39696
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39696
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda: tas2781: Fix wrong reference of tasdevice_priv

During the conversion to unify the calibration data management, the
reference to tasdevice_priv was wrongly set to h->hda_priv instead of
h->priv.  This resulted in memory corruption and crashes eventually.
Unfortunately it's a void pointer, hence the compiler couldn't know
that it's wrong.

## References
- https://git.kernel.org/stable/c/2812815aa79637d39d4398ecd7e58f65d1c79231
- https://git.kernel.org/stable/c/3f4422e7c9436abf81a00270be7e4d6d3760ec0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39696.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
