# [M] ASoC: dapm: fix bounds checker error in dapm_widget_list_create

## Summary
Severity: Medium
Advisory: CVE-2024-53045
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53045
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: dapm: fix bounds checker error in dapm_widget_list_create

The widgets array in the snd_soc_dapm_widget_list has a __counted_by
attribute attached to it, which points to the num_widgets variable. This
attribute is used in bounds checking, and if it is not set before the
array is filled, then the bounds sanitizer will issue a warning or a
kernel panic if CONFIG_UBSAN_TRAP is set.

This patch sets the size of the widgets list calculated with
list_for_each as the initial value for num_widgets as it is used for
allocating memory for the array. It is updated with the actual number of
added elements after the array is filled.

## References
- https://git.kernel.org/stable/c/2ef9439f7a19fd3d43b288d38b1c6e55b668a4fe
- https://git.kernel.org/stable/c/c549cb66e8de0ba1936fc97a59f0156741d3492a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53045.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
