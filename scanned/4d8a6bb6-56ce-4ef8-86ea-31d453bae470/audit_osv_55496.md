# [H] CVE-2025-58148

## Summary
Severity: High
Advisory: CVE-2025-58148
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-58148
Type: osv

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

Some Viridian hypercalls can specify a mask of vCPU IDs as an input, in
one of three formats.  Xen has boundary checking bugs with all three
formats, which can cause out-of-bounds reads and writes while processing
the inputs.

 * CVE-2025-58147.  Hypercalls using the HV_VP_SET Sparse format can
   cause vpmask_set() to write out of bounds when converting the bitmap
   to Xen's format.

 * CVE-2025-58148.  Hypercalls using any input format can cause
   send_ipi() to read d->vcpu[] out-of-bounds, and operate on a wild
   vCPU pointer.

## References
- https://xenbits.xenproject.org/xsa/advisory-475.html
- http://www.openwall.com/lists/oss-security/2025/10/21/1
- http://xenbits.xen.org/xsa/advisory-475.html
