# [H] soc: qcom: llcc: Handle a second device without data corruption

## Summary
Severity: High
Advisory: CVE-2023-52871
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52871
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: qcom: llcc: Handle a second device without data corruption

Usually there is only one llcc device. But if there were a second, even
a failed probe call would modify the global drv_data pointer. So check
if drv_data is valid before overwriting it.

## References
- https://git.kernel.org/stable/c/1143bfb9b055897975aeaea254da148e19524493
- https://git.kernel.org/stable/c/3565684309e54fa998ea27f37028d67cc3e1dff2
- https://git.kernel.org/stable/c/5e5b85ea0f4bc484bfe4cc73ead51fa48d2366a0
- https://git.kernel.org/stable/c/995ee1e84e8db7fa5dcdde7dfe0bd7bb6f9bbb8c
- https://git.kernel.org/stable/c/cc1a1dcb411fe224f48553cfdcdfe6e61395b69c
- https://git.kernel.org/stable/c/f0ef883cae309bc5e8cdfcdbc1b4822732ce20a8
- https://git.kernel.org/stable/c/f1a1bc8775b26345aba2be278118999e7f661d3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52871.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52871
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
