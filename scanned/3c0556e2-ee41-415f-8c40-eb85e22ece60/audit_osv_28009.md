# [H] clk: qcom: gcc-ipq9574: fix terminating of frequency table arrays

## Summary
Severity: High
Advisory: CVE-2024-26968
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26968
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: qcom: gcc-ipq9574: fix terminating of frequency table arrays

The frequency table arrays are supposed to be terminated with an
empty element. Add such entry to the end of the arrays where it
is missing in order to avoid possible out-of-bound access when
the table is traversed by functions like qcom_find_freq() or
qcom_find_freq_floor().

Only compile tested.

## References
- https://git.kernel.org/stable/c/0204247cf3669b6021fb745c3b7f37ae392ab19c
- https://git.kernel.org/stable/c/1723629fea8a4e75333196866e10d395463dca72
- https://git.kernel.org/stable/c/604f2d7c46727c5e24fc7faddc980bc1cc0b1011
- https://git.kernel.org/stable/c/bd2b6395671d823caa38d8e4d752de2448ae61e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26968.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
