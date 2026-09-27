# [H] nvme: apple: fix device reference counting

## Summary
Severity: High
Advisory: CVE-2024-43913
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-43913
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.64, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: apple: fix device reference counting

Drivers must call nvme_uninit_ctrl after a successful nvme_init_ctrl.
Split the allocation side out to make the error handling boundary easier
to navigate. The apple driver had been doing this wrong, leaking the
controller device memory on a tagset failure.

## References
- https://git.kernel.org/stable/c/b9ecbfa45516182cd062fecd286db7907ba84210
- https://git.kernel.org/stable/c/d59c4d0eb6adc24c2201f153ccb7fd0a335b0d3d
- https://git.kernel.org/stable/c/f7d9a18572fcd7130459b7691bd19ee2a2e951ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43913.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43913
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
