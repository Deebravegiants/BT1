# [M] clk: qcom: dispcc-sm6350: Add missing parent_map for a clock

## Summary
Severity: Medium
Advisory: CVE-2024-58080
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58080
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: qcom: dispcc-sm6350: Add missing parent_map for a clock

If a clk_rcg2 has a parent, it should also have parent_map defined,
otherwise we'll get a NULL pointer dereference when calling clk_set_rate
like the following:

  [    3.388105] Call trace:
  [    3.390664]  qcom_find_src_index+0x3c/0x70 (P)
  [    3.395301]  qcom_find_src_index+0x1c/0x70 (L)
  [    3.399934]  _freq_tbl_determine_rate+0x48/0x100
  [    3.404753]  clk_rcg2_determine_rate+0x1c/0x28
  [    3.409387]  clk_core_determine_round_nolock+0x58/0xe4
  [    3.421414]  clk_core_round_rate_nolock+0x48/0xfc
  [    3.432974]  clk_core_round_rate_nolock+0xd0/0xfc
  [    3.444483]  clk_core_set_rate_nolock+0x8c/0x300
  [    3.455886]  clk_set_rate+0x38/0x14c

Add the parent_map property for the clock where it's missing and also
un-inline the parent_data as well to keep the matching parent_map and
parent_data together.

## References
- https://git.kernel.org/stable/c/2dba8d5d423fa5f6f3a687aa6e0da5808f69091b
- https://git.kernel.org/stable/c/3ad28517385e2821e8e43388d6a0b3e1ba0bc3ab
- https://git.kernel.org/stable/c/3daca9050857220726732ad9d4a8512069386f46
- https://git.kernel.org/stable/c/a1f15808adfd77268eac7fefce5378ad9fedbfba
- https://git.kernel.org/stable/c/d4cdb196f182d2fbe336c968228be00d8c3fed05
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58080.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
