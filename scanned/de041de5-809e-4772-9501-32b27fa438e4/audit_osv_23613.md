# [H] drm/dp: Fix OOB read when handling Post Cursor2 register

## Summary
Severity: High
Advisory: CVE-2022-49218
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49218
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/dp: Fix OOB read when handling Post Cursor2 register

The link_status array was not large enough to read the Adjust Request
Post Cursor2 register, so remove the common helper function to avoid
an OOB read, found with a -Warray-bounds build:

drivers/gpu/drm/drm_dp_helper.c: In function 'drm_dp_get_adjust_request_post_cursor':
drivers/gpu/drm/drm_dp_helper.c:59:27: error: array subscript 10 is outside array bounds of 'const u8[6]' {aka 'const unsigned char[6]'} [-Werror=array-bounds]
   59 |         return link_status[r - DP_LANE0_1_STATUS];
      |                ~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~
drivers/gpu/drm/drm_dp_helper.c:147:51: note: while referencing 'link_status'
  147 | u8 drm_dp_get_adjust_request_post_cursor(const u8 link_status[DP_LINK_STATUS_SIZE],
      |                                          ~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace the only user of the helper with an open-coded fetch and decode,
similar to drivers/gpu/drm/amd/display/dc/core/dc_link_dp.c.

## References
- https://git.kernel.org/stable/c/a2151490cc6c57b368d7974ffd447a8b36ade639
- https://git.kernel.org/stable/c/aeaed9a9fe694f8b1462fb81e2d33298c929180b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49218.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49218
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
