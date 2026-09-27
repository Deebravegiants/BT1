# [H] EDAC/qcom: Do not pass llcc_driv_data as edac_device_ctl_info's pvt_info

## Summary
Severity: High
Advisory: CVE-2023-53003
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53003
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

EDAC/qcom: Do not pass llcc_driv_data as edac_device_ctl_info's pvt_info

The memory for llcc_driv_data is allocated by the LLCC driver. But when
it is passed as the private driver info to the EDAC core, it will get freed
during the qcom_edac driver release. So when the qcom_edac driver gets probed
again, it will try to use the freed data leading to the use-after-free bug.

Hence, do not pass llcc_driv_data as pvt_info but rather reference it
using the platform_data pointer in the qcom_edac driver.

## References
- https://git.kernel.org/stable/c/66e10d5f399629ef7877304d9ba2b35d0474e7eb
- https://git.kernel.org/stable/c/6f0351d0c311951b8b3064db91e61841e85b2b96
- https://git.kernel.org/stable/c/76d9ebb7f0bc10fbc78b6d576751552edf743968
- https://git.kernel.org/stable/c/977c6ba624f24ae20cf0faee871257a39348d4a9
- https://git.kernel.org/stable/c/bff5243bd32661cf9ce66f6d9210fc8f89bda145
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53003.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
