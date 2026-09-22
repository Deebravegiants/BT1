# [H] ALSA: hda: intel-sdw-acpi: fix usage of device_get_named_child_node()

## Summary
Severity: High
Advisory: CVE-2024-36955
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36955
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda: intel-sdw-acpi: fix usage of device_get_named_child_node()

The documentation for device_get_named_child_node() mentions this
important point:

"
The caller is responsible for calling fwnode_handle_put() on the
returned fwnode pointer.
"

Add fwnode_handle_put() to avoid a leaked reference.

## References
- https://git.kernel.org/stable/c/722d33c442e66e4aabd3e778958d696ff3a2777e
- https://git.kernel.org/stable/c/7db626d2730d3d80fd31638169054b1e507f07bf
- https://git.kernel.org/stable/c/7ef6ecf98ce309b1f4e5a25cddd5965d01feea07
- https://git.kernel.org/stable/c/bd2d9641a39e6b5244230c4b41c4aca83b54b377
- https://git.kernel.org/stable/c/c158cf914713efc3bcdc25680c7156c48c12ef6a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36955.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36955
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
