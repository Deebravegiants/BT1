# [M] libde265 has an unbounded memory leak via orphaned slice headers in `read_slice_NAL`

## Summary
Severity: Medium
Advisory: CVE-2026-49337
Aliases: GHSA-g5hj-rf9f-7vxm
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-49337
Type: osv

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.20, a crafted sequence of H.265 NAL units causes `decoder_context::read_slice_NAL()` (`libde265/decctx.cc:481`) to attach slice headers to a finished picture object
that has no active image unit, resulting in attacker-controlled unbounded heap growth. The retained headers are never freed until the picture is released, which may not happen during continuous streaming. Version 1.0.20 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49337.json
- https://github.com/strukturag/libde265/security/advisories/GHSA-g5hj-rf9f-7vxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-49337
- https://github.com/strukturag/libde265/commit/683cb9fa603e35840642f98765ab95cdb71cadf9
