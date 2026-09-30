# [H] crypto: iaa - Fix potential use after free bug

## Summary
Severity: High
Advisory: CVE-2024-47732
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47732
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: iaa - Fix potential use after free bug

The free_device_compression_mode(iaa_device, device_mode) function frees
"device_mode" but it iss passed to iaa_compression_modes[i]->free() a few
lines later resulting in a use after free.

The good news is that, so far as I can tell, nothing implements the
->free() function and the use after free happens in dead code.  But, with
this fix, when something does implement it, we'll be ready.  :)

## References
- https://git.kernel.org/stable/c/b5d534b473e2c8d3e4560be2dd6c12a8eb9d61e9
- https://git.kernel.org/stable/c/c66f0be993ba52410edab06124c54ecf143b05c1
- https://git.kernel.org/stable/c/e0d3b845a1b10b7b5abdad7ecc69d45b2aab3209
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47732.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47732
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
