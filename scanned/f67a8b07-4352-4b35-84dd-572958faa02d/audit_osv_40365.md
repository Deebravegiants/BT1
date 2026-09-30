# [C] ocfs2/dlm: validate qr_numregions in dlm_match_regions()

## Summary
Severity: Critical
Advisory: CVE-2026-53043
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53043
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2/dlm: validate qr_numregions in dlm_match_regions()

Patch series "ocfs2/dlm: fix two bugs in dlm_match_regions()".

In dlm_match_regions(), the qr_numregions field from a DLM_QUERY_REGION
network message is used to drive loops over the qr_regions buffer without
sufficient validation.  This series fixes two issues:

- Patch 1 adds a bounds check to reject messages where qr_numregions
  exceeds O2NM_MAX_REGIONS. The o2net layer only validates message
  byte length; it does not constrain field values, so a crafted message
  can set qr_numregions up to 255 and trigger out-of-bounds reads past
  the 1024-byte qr_regions buffer.

- Patch 2 fixes an off-by-one in the local-vs-remote comparison loop,
  which uses '<=' instead of '<', reading one entry past the valid range
  even when qr_numregions is within bounds.


This patch (of 2):

The qr_numregions field from a DLM_QUERY_REGION network message is used
directly as loop bounds in dlm_match_regions() without checking against
O2NM_MAX_REGIONS.  Since qr_regions is sized for at most O2NM_MAX_REGIONS
(32) entries, a crafted message with qr_numregions > 32 causes
out-of-bounds reads past the qr_regions buffer.

Add a bounds check for qr_numregions before entering the loops.

## References
- https://git.kernel.org/stable/c/1f8b91275912cd428289c1fb424bebd7ff5302bd
- https://git.kernel.org/stable/c/3c2d0de23ae4be22b6c18e8f0915be74d3b5fb21
- https://git.kernel.org/stable/c/3f474c33ebc2e2ca3fcb587d7de4375348f13373
- https://git.kernel.org/stable/c/6c6e8fc3c007319981647b410c29bb5775048551
- https://git.kernel.org/stable/c/7ab3fbb01bc6d79091bc375e5235d360cd9b78be
- https://git.kernel.org/stable/c/d3d5efade0c79dac1cac98c0cb1115432f804439
- https://git.kernel.org/stable/c/f37de46149db49abd2b24f4f0c5a88cf4dfb5f47
- https://git.kernel.org/stable/c/f69551139caf6d24242a0ad049ee46b264e3aee0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53043.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
