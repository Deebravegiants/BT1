# [H] drm/amd/display: Ensure array index tg_inst won't be -1

## Summary
Severity: High
Advisory: CVE-2024-46730
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46730
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Ensure array index tg_inst won't be -1

[WHY & HOW]
tg_inst will be a negative if timing_generator_count equals 0, which
should be checked before used.

This fixes 2 OVERRUN issues reported by Coverity.

## References
- https://git.kernel.org/stable/c/687fe329f18ab0ab0496b20ed2cb003d4879d931
- https://git.kernel.org/stable/c/a64284b9e1999ad5580debced4bc6d6adb28aad4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46730.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
