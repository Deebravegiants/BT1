# [H] ALSA: virtio: Validate control metadata from the device

## Summary
Severity: High
Advisory: CVE-2026-64490
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64490
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: virtio: Validate control metadata from the device

virtio-snd control handling trusts the device-provided control type and
value count returned by the device.

That metadata is then used directly to index g_v2a_type_map[] in
virtsnd_kctl_info(), and to size loops and memcpy() operations in
virtsnd_kctl_get() and virtsnd_kctl_put() against fixed-size
virtio_snd_ctl_value and snd_ctl_elem_value arrays.

A buggy or malicious device can therefore trigger out-of-bounds access by
advertising an invalid control type or an oversized value count.

Validate control type and count once in virtsnd_kctl_parse_cfg(), before
querying enumerated items or exposing the control to ALSA.

## References
- https://git.kernel.org/stable/c/21584672fd699abe1768241d6c501b2de6139b6a
- https://git.kernel.org/stable/c/3243563f99ef5d3949b934bd6390a5679405d0e1
- https://git.kernel.org/stable/c/5da9742de22db0dbaa8d414214ab5e1bedde00f9
- https://git.kernel.org/stable/c/c77a6cbb36ff8cbc1f084d94f8dcda5250935271
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64490.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
