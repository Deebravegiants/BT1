# [M] cxl/region: Fix decoder allocation crash

## Summary
Severity: Medium
Advisory: CVE-2022-49895
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49895
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/region: Fix decoder allocation crash

When an intermediate port's decoders have been exhausted by existing
regions, and creating a new region with the port in question in it's
hierarchical path is attempted, cxl_port_attach_region() fails to find a
port decoder (as would be expected), and drops into the failure / cleanup
path.

However, during cleanup of the region reference, a sanity check attempts
to dereference the decoder, which in the above case didn't exist. This
causes a NULL pointer dereference BUG.

To fix this, refactor the decoder allocation and de-allocation into
helper routines, and in this 'free' routine, check that the decoder,
@cxld, is valid before attempting any operations on it.

## References
- https://git.kernel.org/stable/c/71ee71d7adcba648077997a29a91158d20c40b09
- https://git.kernel.org/stable/c/c6813b5610ac53af73edd87a660d23a0511faa47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49895.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49895
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
