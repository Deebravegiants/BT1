# [H] drm/virtio: bound EDID block reads to the response buffer

## Summary
Severity: High
Advisory: CVE-2026-68255
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68255
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/virtio: bound EDID block reads to the response buffer

virtio_get_edid_block() validates the read offset only against the
device-supplied resp->size field, never against the fixed-size resp->edid
array. The EDID block index is driven by the device-supplied extension
count, so a malicious virtio-gpu backend can advertise a large size
together with a high block count and read far past the array into adjacent
kernel memory, which is then surfaced in the parsed EDID (an out-of-bounds
read / info leak).

Also reject any read whose end exceeds the size of the edid array.
Conforming EDID responses stay within the array and are unaffected.

## References
- https://git.kernel.org/stable/c/2757e6e803092cf0aeaf4b735e16b5d3bdc705c5
- https://git.kernel.org/stable/c/35be0e2c6862abcd5e5f5445261f1fd910d4a9b4
- https://git.kernel.org/stable/c/375c1934ef0196d3b6d3a1eae3232bef8dae7bf7
- https://git.kernel.org/stable/c/3f506a85a905b080cadc029a1651a310479090a6
- https://git.kernel.org/stable/c/4e1a53892ba7f8a3e1da6bfc53c83ae7c812dccd
- https://git.kernel.org/stable/c/64bedd2758eccbc74d39f7006a7ec16fa39dc901
- https://git.kernel.org/stable/c/65ce911f341ad8ff0c08922eff5bb6db75666eb0
- https://git.kernel.org/stable/c/9fc2a017c5d597937e0c28b9a9669844aa796c42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68255.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
