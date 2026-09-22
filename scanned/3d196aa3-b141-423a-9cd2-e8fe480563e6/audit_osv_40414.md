# [H] accel/ethosu: fix IFM region index out-of-bounds in command stream parser

## Summary
Severity: High
Advisory: CVE-2026-53172
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53172
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ethosu: fix IFM region index out-of-bounds in command stream parser

NPU_SET_IFM_REGION extracts the region index with param & 0x7f, giving
a maximum value of 127. However region_size[] and output_region[] in
struct ethosu_validated_cmdstream_info are both sized to
NPU_BASEP_REGION_MAX (8), giving valid indices [0..7].

Every other region assignment in the same switch uses param & 0x7:
  NPU_SET_OFM_REGION:  st.ofm.region  = param & 0x7;
  NPU_SET_IFM2_REGION: st.ifm2.region = param & 0x7;
  NPU_SET_WEIGHT_REGION: st.weight[0].region = param & 0x7;
  NPU_SET_SCALE_REGION:  st.scale[0].region  = param & 0x7;

The 0x7f mask on IFM is inconsistent and appears to be a typo.

feat_matrix_length() and calc_sizes() use the region index directly
as an array subscript into the kzalloc'd info struct:
  info->region_size[fm->region] = max(...);

A userspace caller supplying NPU_SET_IFM_REGION with param > 7 causes
a write up to 127*8 = 1016 bytes past the start of region_size[],
corrupting adjacent kernel heap data.

Fix by applying the same & 0x7 mask used by all other region
assignments.

## References
- https://git.kernel.org/stable/c/00f547e0dfecf83014fb32bcba587c6b684c1362
- https://git.kernel.org/stable/c/ee7bed779def61ebff1b92b0e851f412176fa416
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
