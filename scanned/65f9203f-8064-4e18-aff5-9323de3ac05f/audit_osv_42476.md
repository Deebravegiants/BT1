# [H] media: amlogic-c3: Add validations for ae and awb config

## Summary
Severity: High
Advisory: CVE-2026-68230
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68230
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: amlogic-c3: Add validations for ae and awb config

Avoid invalid memory access if the zones_num is bigger than
zone_weight.

This patch fixes the following smatch errors:
drivers/media/platform/amlogic/c3/isp/c3-isp-params.c:111 c3_isp_params_awb_wt() error: buffer overflow 'cfg->zone_weight' 768 <= u32max
drivers/media/platform/amlogic/c3/isp/c3-isp-params.c:111 c3_isp_params_awb_wt() error: buffer overflow 'cfg->zone_weight' 768 <= u32max
drivers/media/platform/amlogic/c3/isp/c3-isp-params.c:227 c3_isp_params_ae_wt() error: buffer overflow 'cfg->zone_weight' 255 <= u32max
drivers/media/platform/amlogic/c3/isp/c3-isp-params.c:227 c3_isp_params_ae_wt() error: buffer overflow 'cfg->zone_weight' 255 <= u32max

## References
- https://git.kernel.org/stable/c/32cbe5474e74817aa8a576b94135cc45e59f5e07
- https://git.kernel.org/stable/c/391fe3e36e59f3c6e3d46edfb3a5de51e00cd216
- https://git.kernel.org/stable/c/9724164f71974a2a44a5e026614fbcc05bab6d91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68230.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
