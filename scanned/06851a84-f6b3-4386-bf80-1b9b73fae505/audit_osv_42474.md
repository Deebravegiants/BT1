# [H] media: cedrus: skip invalid H.264 reference list entries

## Summary
Severity: High
Advisory: CVE-2026-68229
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68229
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: cedrus: skip invalid H.264 reference list entries

Cedrus consumes H.264 ref_pic_list0/ref_pic_list1 entries from the
stateless slice control and later uses their indices to look up
decode->dpb[] in _cedrus_write_ref_list().

Rejecting such controls in cedrus_try_ctrl() would break existing
userspace, since stateless H.264 reference lists may legitimately carry
out-of-range indices for missing references. Instead, guard the actual
DPB lookup in Cedrus and skip entries whose indices do not fit the fixed
V4L2_H264_NUM_DPB_ENTRIES array.

This keeps the fix local to the driver use site and avoids out-of-bounds
reads from malformed or unsupported reference list entries.

## References
- https://git.kernel.org/stable/c/0af8945fcae742d099f59f3c725eb67235953a31
- https://git.kernel.org/stable/c/10358ea986c3c85516d1c8206486464f79d36e76
- https://git.kernel.org/stable/c/1db34683b0fbbcb3bc162380c11514ea0a44e8ab
- https://git.kernel.org/stable/c/2ee8327c85b3ac7b532d2d6a1e3a295d5ad7414a
- https://git.kernel.org/stable/c/7ff6f728a2433b420bb372cb0e8a4eea3f2e1a4b
- https://git.kernel.org/stable/c/9924cb548ee7753a6473997949c3ec48092de0b0
- https://git.kernel.org/stable/c/a6a109771c51920beb620f30778c29da823cc34c
- https://git.kernel.org/stable/c/e53112c2de88982e66c369aee2120d5efd78df30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68229.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68229
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
