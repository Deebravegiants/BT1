# [H] bpf: Preserve pointer state for commuted arithmetic

## Summary
Severity: High
Advisory: CVE-2026-74720
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74720
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Preserve pointer state for commuted arithmetic

When scalar += pointer is handled in adjust_ptr_min_max_vals(), the
destination register inherits the pointer state from the source pointer.
Copying only selected fields is fragile because pointer provenance is
tracked by several bpf_reg_state fields.

Use the caller's temporary offset register to preserve the scalar operand
while replacing the destination with the full pointer state. This preserves
the frame number for PTR_TO_STACK registers and keeps parent identity
fields consistent.

## References
- https://git.kernel.org/stable/c/29c239f8dbec5ab33a61796724d189bddee6cd4b
- https://git.kernel.org/stable/c/8109c25e0c41f5f19a1c2380bb49c991a877494e
- https://git.kernel.org/stable/c/86b203aadc2930e0a4f9c6277b5b80ff3664c472
- https://git.kernel.org/stable/c/8cb23101a3fcc7432b451ea3d0f14a90711f4acf
- https://git.kernel.org/stable/c/a4c6f804b44c5c790269b25e0e61cf4e9f117c86
- https://git.kernel.org/stable/c/d1959028190a7649b926f5867a58de5fe221b23c
- https://git.kernel.org/stable/c/db6382ed3361bdd8129572a3423956cba1dae829
- https://git.kernel.org/stable/c/eaffa1495e4fe6330aeff9f323ea3d48b01f118a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74720.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74720
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
