# [M] drm: xlnx: zynqmp_disp: layer may be null while releasing

## Summary
Severity: Medium
Advisory: CVE-2024-56537
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56537
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: xlnx: zynqmp_disp: layer may be null while releasing

layer->info can be null if we have an error on the first layer in
zynqmp_disp_create_layers

## References
- https://git.kernel.org/stable/c/223842c7702b52846b1c5aef8aca7474ec1fd29b
- https://git.kernel.org/stable/c/9218be402aeb1999cc119fc616e21c3cc7cdeec0
- https://git.kernel.org/stable/c/ce7e62bbd55d20cf250396eb4e8f65b3b5a5e685
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56537.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56537
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
