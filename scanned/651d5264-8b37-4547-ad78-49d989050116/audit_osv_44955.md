# [C] CVE-2026-89086

## Summary
Severity: Critical
Advisory: CVE-2026-89086
Aliases: OSEC-2026-19
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-89086
Type: osv

## Details
In the jose package before 0.11.0 for OCaml, library calls to validate an RSA signature only confirm that PKCS #1 decoding succeeds, and proceed to declare the signature valid without the required steps that involve the public key.

## References
- https://osv.dev/vulnerability/OSEC-2026-19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89086.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-89086
- https://github.com/ulrikstrid/ocaml-jose/commit/cf17d991ec6a0d1997956b6c7799890f9c28879e
