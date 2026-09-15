# [H] ASoC: tas2562: Validate values for volume writes

## Summary
Severity: High
Advisory: CVE-2026-80526
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80526
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: tas2562: Validate values for volume writes

tas2562_volume_control_put() does not do any validation of the control
value written by userspace, it uses it to look up a value in a fixed
size array which can easily be overflowed and then writes whatever value
it gets back to the device.  Add validation that we are loading a value
we have in the array.

## References
- https://git.kernel.org/stable/c/1f389ecd0c35e9e281036e44c121df904f3164c1
- https://git.kernel.org/stable/c/20bdbb1376457ecbf418bf677fd285820d1fc011
- https://git.kernel.org/stable/c/8fb41964f7e4e4207c8999af2056894caa7a252a
- https://git.kernel.org/stable/c/c37a0461c0d0a70c5de4fdbd70449a7f53c12dda
- https://git.kernel.org/stable/c/db488d653d896fcf9ac87e15239924c2928bbc3c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80526.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80526
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
