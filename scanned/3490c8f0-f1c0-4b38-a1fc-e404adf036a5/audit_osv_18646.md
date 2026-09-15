# [H] CVE-2020-29529

## Summary
Severity: High
Advisory: CVE-2020-29529
Aliases: GHSA-2g5j-5x95-r6hr, GO-2021-0094
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-29529
Type: osv

## Details
HashiCorp go-slug up to 0.4.3 did not fully protect against directory traversal while unpacking tar archives, and protections could be bypassed with specific constructions of multiple symlinks. Fixed in 0.5.0.

## References
- https://github.com/hashicorp/go-slug/releases/tag/v0.5.0
- https://github.com/hashicorp/go-slug/compare/v0.4.3...v0.5.0
- https://github.com/hashicorp/go-slug/pull/12
- https://securitylab.github.com/advisories/GHSL-2020-262-zipslip-go-slug
