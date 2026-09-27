# [H] drm/amd/display: Increase block_sequence array size

## Summary
Severity: High
Advisory: CVE-2025-38080
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38080
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Increase block_sequence array size

[Why]
It's possible to generate more than 50 steps in hwss_build_fast_sequence,
for example with a 6-pipe asic where all pipes are in one MPC chain. This
overflows the block_sequence buffer and corrupts block_sequence_steps,
causing a crash.

[How]
Expand block_sequence to 100 items. A naive upper bound on the possible
number of steps for a 6-pipe asic, ignoring the potential for steps to be
mutually exclusive, is 91 with current code, therefore 100 is sufficient.

## References
- https://git.kernel.org/stable/c/3a7810c212bcf2f722671dadf4b23ff70a7d23ee
- https://git.kernel.org/stable/c/bf1666072e7482317cf2302621766482a21a62c7
- https://git.kernel.org/stable/c/de67e80ab48f1f23663831007a2fa3c1471a7757
- https://git.kernel.org/stable/c/e55c5704b12eeea27e212bfab8f7e51ad3e8ac1f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38080.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
