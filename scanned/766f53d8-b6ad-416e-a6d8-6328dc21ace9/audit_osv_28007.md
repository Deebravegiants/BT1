# [H] clk: qcom: mmcc-msm8974: fix terminating of frequency table arrays

## Summary
Severity: High
Advisory: CVE-2024-26965
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26965
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: qcom: mmcc-msm8974: fix terminating of frequency table arrays

The frequency table arrays are supposed to be terminated with an
empty element. Add such entry to the end of the arrays where it
is missing in order to avoid possible out-of-bound access when
the table is traversed by functions like qcom_find_freq() or
qcom_find_freq_floor().

Only compile tested.

## References
- https://git.kernel.org/stable/c/3ff4a0f6a8f0ad4b4ee9e908bdfc3cacb7be4060
- https://git.kernel.org/stable/c/537040c257ab4cd0673fbae048f3940c8ea2e589
- https://git.kernel.org/stable/c/7e9926fef71e514b4a8ea9d11d5a84d52b181362
- https://git.kernel.org/stable/c/86bf75d9158f511db7530bc82a84b19a5134d089
- https://git.kernel.org/stable/c/8f562f3b25177c2055b20fd8cf000496f6fa9194
- https://git.kernel.org/stable/c/99740c4791dc8019b0d758c5389ca6d1c0604d95
- https://git.kernel.org/stable/c/ae99e199037c580b7350bfa3596f447a53bcf01f
- https://git.kernel.org/stable/c/ca2cf98d46748373e830a13d85d215d64a2d9bf2
- https://git.kernel.org/stable/c/e2c02a85bf53ae86d79b5fccf0a75ac0b78e0c96
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26965.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26965
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
