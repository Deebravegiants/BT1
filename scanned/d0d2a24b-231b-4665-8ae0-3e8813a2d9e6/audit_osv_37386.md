# [H] scsi: ibmvfc: Fix OOB access in ibmvfc_discover_targets_done()

## Summary
Severity: High
Advisory: CVE-2026-31464
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31464
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ibmvfc: Fix OOB access in ibmvfc_discover_targets_done()

A malicious or compromised VIO server can return a num_written value in the
discover targets MAD response that exceeds max_targets. This value is
stored directly in vhost->num_targets without validation, and is then used
as the loop bound in ibmvfc_alloc_targets() to index into disc_buf[], which
is only allocated for max_targets entries. Indices at or beyond max_targets
access kernel memory outside the DMA-coherent allocation.  The
out-of-bounds data is subsequently embedded in Implicit Logout and PLOGI
MADs that are sent back to the VIO server, leaking kernel memory.

Fix by clamping num_written to max_targets before storing it.

## References
- https://git.kernel.org/stable/c/394a1cac3c12fdd7d77f19ccfd222ab5ff87ef89
- https://git.kernel.org/stable/c/4ed727e35b0ab17d3eeeb1e8023768396e2be161
- https://git.kernel.org/stable/c/61d099ac4a7a8fb11ebdb6e2ec8d77f38e77362f
- https://git.kernel.org/stable/c/786f10b1966e485046839f992e89f2c18cbd1983
- https://git.kernel.org/stable/c/a007246cb6c9ebdc93dafbf63cc2d43d98f402cc
- https://git.kernel.org/stable/c/bae4df0a643fa7f84663473aa3082a9c2ed139db
- https://git.kernel.org/stable/c/d1466bf991b2343cf2ba8336e440c8faf3cbb780
- https://git.kernel.org/stable/c/d842348f8a00d5b1d7358f207eb34ffcf5b16df3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31464.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31464
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
