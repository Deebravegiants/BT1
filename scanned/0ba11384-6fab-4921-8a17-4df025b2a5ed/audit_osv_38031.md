# [M] CVE-2026-34353

## Summary
Severity: Medium
Advisory: CVE-2026-34353
Aliases: OSEC-2026-04
CVSS: 5.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-34353
Type: osv

## Details
In OCaml through 4.14.3, Bigarray.reshape allows an integer overflow, and resultant reading of arbitrary memory, when untrusted data is processed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34353.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34353
- https://github.com/ocaml/ocaml/issues/14655
- https://github.com/ocaml/ocaml/pull/14674
