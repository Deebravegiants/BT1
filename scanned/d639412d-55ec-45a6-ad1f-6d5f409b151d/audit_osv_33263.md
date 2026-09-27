# [H] i40e: fix validation of VF state in get resources

## Summary
Severity: High
Advisory: CVE-2025-39969
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39969
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.6.109, >=6.2.0 <6.12.50, >=6.7.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: fix validation of VF state in get resources

VF state I40E_VF_STATE_ACTIVE is not the only state in which
VF is actually active so it should not be used to determine
if a VF is allowed to obtain resources.

Use I40E_VF_STATE_RESOURCES_LOADED that is set only in
i40e_vc_get_vf_resources_msg() and cleared during reset.

## References
- https://git.kernel.org/stable/c/185745d56ec958bf8aa773828213237dfcc32f5a
- https://git.kernel.org/stable/c/6128bbc7adc25c87c2f64b5eb66a280b78ef7ab7
- https://git.kernel.org/stable/c/6c3981fd59ef11a75005ac9978f034da5a168b6a
- https://git.kernel.org/stable/c/877b7e6ffc23766448236e8732254534c518ba42
- https://git.kernel.org/stable/c/8e35c80f8570426fe0f0cc92b151ebd835975f22
- https://git.kernel.org/stable/c/a991dc56d3e9a2c3db87d0c3f03c24f6595400f1
- https://git.kernel.org/stable/c/e748f1ee493f88e38b77363a60499f979d42c58a
- https://git.kernel.org/stable/c/f47876788a23de296c42ef9d505b5c1630f0b4b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39969.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39969
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
