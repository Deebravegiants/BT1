# [H] scsi: target: Fix NULL pointer dereference in core_scsi3_decode_spec_i_port()

## Summary
Severity: High
Advisory: CVE-2025-38399
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38399
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: Fix NULL pointer dereference in core_scsi3_decode_spec_i_port()

The function core_scsi3_decode_spec_i_port(), in its error code path,
unconditionally calls core_scsi3_lunacl_undepend_item() passing the
dest_se_deve pointer, which may be NULL.

This can lead to a NULL pointer dereference if dest_se_deve remains
unset.

SPC-3 PR SPEC_I_PT: Unable to locate dest_tpg
Unable to handle kernel paging request at virtual address dfff800000000012
Call trace:
  core_scsi3_lunacl_undepend_item+0x2c/0xf0 [target_core_mod] (P)
  core_scsi3_decode_spec_i_port+0x120c/0x1c30 [target_core_mod]
  core_scsi3_emulate_pro_register+0x6b8/0xcd8 [target_core_mod]
  target_scsi3_emulate_pr_out+0x56c/0x840 [target_core_mod]

Fix this by adding a NULL check before calling
core_scsi3_lunacl_undepend_item()

## References
- https://git.kernel.org/stable/c/1129e0e0a833acf90429e0f13951068d5f026e4f
- https://git.kernel.org/stable/c/1627dda4d70ceb1ba62af2e401af73c09abb1eb5
- https://git.kernel.org/stable/c/55dfffc5e94730370b08de02c0cf3b7c951bbe9e
- https://git.kernel.org/stable/c/70ddb8133fdb512d4b1f2b4fd1c9e518514f182c
- https://git.kernel.org/stable/c/7296c938df2445f342be456a6ff0b3931d97f4e5
- https://git.kernel.org/stable/c/c412185d557578d3f936537ed639c4ffaaed4075
- https://git.kernel.org/stable/c/d8ab68bdb294b09a761e967dad374f2965e1913f
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38399.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
