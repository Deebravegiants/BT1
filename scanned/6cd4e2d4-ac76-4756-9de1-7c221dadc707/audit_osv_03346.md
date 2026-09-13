# [H] ALPINE-CVE-2025-58148

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-58148
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58148
Type: osv

## Affected
- Alpine:v3.19: `xen` — affected >=4.15.0 <4.18.5-r3
- Alpine:v3.20: `xen` — affected >=4.15.0 <4.18.5-r3
- Alpine:v3.21: `xen` — affected >=4.15.0 <4.19.3-r2
- Alpine:v3.22: `xen` — affected >=4.15.0 <4.20.1-r2
- Alpine:v3.23: `xen` — affected >=4.15.0 <4.20.1-r2
- Alpine:v3.24: `xen` — affected >=4.15.0 <4.20.1-r2

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
- https://security.alpinelinux.org/vuln/CVE-2025-58148
