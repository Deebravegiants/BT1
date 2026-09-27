# [H] drm/amd/display: Handle dml allocation failure to avoid crash

## Summary
Severity: High
Advisory: CVE-2024-53133
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53133
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Handle dml allocation failure to avoid crash

[Why]
In the case where a dml allocation fails for any reason, the
current state's dml contexts would no longer be valid. Then
subsequent calls dc_state_copy_internal would shallow copy
invalid memory and if the new state was released, a double
free would occur.

[How]
Reset dml pointers in new_state to NULL and avoid invalid
pointer

(cherry picked from commit bcafdc61529a48f6f06355d78eb41b3aeda5296c)

## References
- https://git.kernel.org/stable/c/6825cb07b79ffeb1d90ffaa7a1227462cdca34ae
- https://git.kernel.org/stable/c/874ff59cde8fc525112dda26b501a1bac17dde9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53133.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
