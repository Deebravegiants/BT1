# [H] Input: synaptics-rmi4 - bound the F30 keymap to the GPIO/LED count

## Summary
Severity: High
Advisory: CVE-2026-64276
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64276
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: synaptics-rmi4 - bound the F30 keymap to the GPIO/LED count

rmi_f30_map_gpios() allocates gpioled_key_map with
min(gpioled_count, TRACKSTICK_RANGE_END) == at most 6 entries, but
rmi_f30_attention() iterates the full f30->gpioled_count (device query
register, range 0..31) and dereferences gpioled_key_map[i], and
input->keycodemax is set to the full gpioled_count while input->keycode
points at the 6-entry allocation.

A device that reports gpioled_count > 6 with GPIO support enabled
therefore causes an out-of-bounds read on the attention interrupt and
out-of-bounds read/write through the EVIOCGKEYCODE/EVIOCSKEYCODE ioctls,
which bound the index only against keycodemax. This is the same defect
as the F3A handler, which was copied from F30.

Size the keymap for the full gpioled_count; the mapping loop still
assigns only the first min(gpioled_count, TRACKSTICK_RANGE_END) entries.

## References
- https://git.kernel.org/stable/c/26c895928d7118436a24f564587cb4aefc40cdd8
- https://git.kernel.org/stable/c/4e3689c26854356f41fbaa1eafa382e58ac79e00
- https://git.kernel.org/stable/c/8c6d18d61bb6fe0e6edf848413391c590552e8a9
- https://git.kernel.org/stable/c/bfe622efecd4ff0a792d0ecd1a8dce535a902f50
- https://git.kernel.org/stable/c/d162a1ead7de404d8b41a093c83ed0db6487cded
- https://git.kernel.org/stable/c/d577e46785d45484b2ab7e7309c49b18764bf56c
- https://git.kernel.org/stable/c/e849c6f51e6877104c765da084e001ec37c8e119
- https://git.kernel.org/stable/c/f0be9eba946e9200b43265e0a748d38bd0a56954
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64276.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
