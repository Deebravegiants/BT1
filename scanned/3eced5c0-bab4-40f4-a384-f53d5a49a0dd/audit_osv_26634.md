# [M] remoteproc: imx_dsp_rproc: Add custom memory copy implementation for i.MX DSP Cores

## Summary
Severity: Medium
Advisory: CVE-2023-53434
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53434
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

remoteproc: imx_dsp_rproc: Add custom memory copy implementation for i.MX DSP Cores

The IRAM is part of the HiFi DSP.
According to hardware specification only 32-bits write are allowed
otherwise we get a Kernel panic.

Therefore add a custom memory copy and memset functions to deal with
the above restriction.

## References
- https://git.kernel.org/stable/c/331cd77f3d02c35f98b48d1aa934c54c4e7102c8
- https://git.kernel.org/stable/c/408ec1ff0caa340c57eecf4cbd14ef0132036a50
- https://git.kernel.org/stable/c/44361033a8806aabd0f49b24e5a2fc07232cc5ff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53434.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
