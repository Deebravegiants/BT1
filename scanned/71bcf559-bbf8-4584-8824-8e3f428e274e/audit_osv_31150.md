# [M] clk: qcom: gcc-sm6350: Add missing parent_map for two clocks

## Summary
Severity: Medium
Advisory: CVE-2024-58076
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58076
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: qcom: gcc-sm6350: Add missing parent_map for two clocks

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

Add the parent_map property for two clocks where it's missing and also
un-inline the parent_data as well to keep the matching parent_map and
parent_data together.

## References
- https://git.kernel.org/stable/c/08b77ed7cfaac62bba51ac7a0487409ec9fcbc84
- https://git.kernel.org/stable/c/175af15551ed5aa6af16ff97aff75cfffb42da21
- https://git.kernel.org/stable/c/39336edd14a59dc086fb19957655e0f340bb28e8
- https://git.kernel.org/stable/c/3e567032233a240b903dc11c9f18eeb3faa10ffa
- https://git.kernel.org/stable/c/96fe1a7ee477d701cfc98ab9d3c730c35d966861
- https://git.kernel.org/stable/c/b6fe13566bf5676b1e3b72d2a06d875733e93ee6
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58076.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
