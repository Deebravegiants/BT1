# [H] ASoC: SOF: ipc3-control: Validate size in snd_sof_update_control

## Summary
Severity: High
Advisory: CVE-2026-72261
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72261
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc3-control: Validate size in snd_sof_update_control

In snd_sof_update_control(), firmware-provided cdata->num_elems is
checked against local_cdata->data->size but never against the actual
allocation size. If local_cdata->data->size was previously set to an
inconsistent value, the memcpy could write past the allocated buffer.

Add a bounds check to ensure num_elems fits within the available space
in the ipc_control_data allocation before copying.

## References
- https://git.kernel.org/stable/c/1dc25a3e06364f48c4ef06016852f8b82425151a
- https://git.kernel.org/stable/c/2a591bf6fd41fd14bdae689aafac4a9ee702c23c
- https://git.kernel.org/stable/c/390aa4c9339bb0ec0bc8d554e830faf93ca9d49e
- https://git.kernel.org/stable/c/d3abaedf6a58469610136d2dace1a85cddf7afcf
- https://git.kernel.org/stable/c/ecf67f1302f2080b4d241b973364aacda70ad740
- https://git.kernel.org/stable/c/ee781058cd4d71e4449f41cbe6a3b8c59daa2c51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72261.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72261
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
