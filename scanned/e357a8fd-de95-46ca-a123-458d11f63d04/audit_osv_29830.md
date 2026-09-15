# [H] ASoC: Intel: soc-acpi-intel-mtl-match: add missing empty item

## Summary
Severity: High
Advisory: CVE-2024-46862
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46862
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: Intel: soc-acpi-intel-mtl-match: add missing empty item

There is no links_num in struct snd_soc_acpi_mach {}, and we test
!link->num_adr as a condition to end the loop in hda_sdw_machine_select().
So an empty item in struct snd_soc_acpi_link_adr array is required.

## References
- https://git.kernel.org/stable/c/01281a9e8275946aa725db0919769b8d35af3a11
- https://git.kernel.org/stable/c/bf6d7a44a144aa9c476dee83c23faf3151181bab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46862.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
