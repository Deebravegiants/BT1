# [M] drm/msm/dp: populate connector of struct dp_panel

## Summary
Severity: Medium
Advisory: CVE-2022-49221
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49221
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.110, >=5.11.0 <5.15.33, >=5.15.0 <5.16.19, >=5.16.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dp: populate connector of struct dp_panel

DP CTS test case 4.2.2.6 has valid edid with bad checksum on purpose
and expect DP source return correct checksum. During drm edid read,
correct edid checksum is calculated and stored at
connector::real_edid_checksum.

The problem is struct dp_panel::connector never be assigned, instead the
connector is stored in struct msm_dp::connector. When we run compliance
testing test case 4.2.2.6 dp_panel_handle_sink_request() won't have a valid
edid set in struct dp_panel::edid so we'll try to use the connectors
real_edid_checksum and hit a NULL pointer dereference error because the
connector pointer is never assigned.

Changes in V2:
-- populate panel connector at msm_dp_modeset_init() instead of at dp_panel_read_sink_caps()

Changes in V3:
-- remove unhelpful kernel crash trace commit text
-- remove renaming dp_display parameter to dp

Changes in V4:
-- add more details to commit text

Changes in v10:
--  group into one series

Changes in v11:
-- drop drm/msm/dp: dp_link_parse_sink_count() return immediately if aux read

Signee-off-by: Kuogee Hsieh <quic_khsieh@quicinc.com>

## References
- https://git.kernel.org/stable/c/104074ebc0c3f358dd1ee944fbcde92c6e5a21dd
- https://git.kernel.org/stable/c/413c62697b61226a236c8b1f5cd64dcf42bcc12f
- https://git.kernel.org/stable/c/5e602f5156910c7b19661699896cb6e3fb94fab9
- https://git.kernel.org/stable/c/9525b8bcae8b99188990b56484799cf4b1b43786
- https://git.kernel.org/stable/c/fbba600f432a360b42452fee79d1fb35d3aa8aeb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49221.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
