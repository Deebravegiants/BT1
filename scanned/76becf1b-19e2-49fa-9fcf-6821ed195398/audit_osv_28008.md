# [H] clk: qcom: camcc-sc8280xp: fix terminating of frequency table arrays

## Summary
Severity: High
Advisory: CVE-2024-26967
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26967
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: qcom: camcc-sc8280xp: fix terminating of frequency table arrays

The frequency table arrays are supposed to be terminated with an
empty element. Add such entry to the end of the arrays where it
is missing in order to avoid possible out-of-bound access when
the table is traversed by functions like qcom_find_freq() or
qcom_find_freq_floor().

Only compile tested.

## References
- https://git.kernel.org/stable/c/6a3d70f7802a98e6c28a74f997a264118b9f50cd
- https://git.kernel.org/stable/c/93ff48729211dae55df5d216023be4528d29babb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26967.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26967
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
