# [M] usb: dwc3: core: fix some leaks in probe

## Summary
Severity: Medium
Advisory: CVE-2022-50357
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50357
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: core: fix some leaks in probe

The dwc3_get_properties() function calls:

	dwc->usb_psy = power_supply_get_by_name(usb_psy_name);

so there is some additional clean up required on these error paths.

## References
- https://git.kernel.org/stable/c/2a735e4b5580a2a6bbd6572109b4c4f163c57462
- https://git.kernel.org/stable/c/3a213503f483173e7eea76f2e7e3bdd6df7fd6f8
- https://git.kernel.org/stable/c/79c3afb55942368921237d7b5355d48c52bdde20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50357.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50357
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
