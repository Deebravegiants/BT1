# [H] teklifolustur_app's IDOR vulnerability allows unauthorized access to other users' offers

## Summary
Severity: High
Advisory: CVE-2026-23843
Aliases: GHSA-6h9r-mmg3-cg7m
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23843
Type: osv

## Details
teklifolustur_app is a web-based PHP application that allows users to create, manage, and track quotes for their clients. Prior to commit dd082a134a225b8dcd401b6224eead4fb183ea1c, an Insecure Direct Object Reference (IDOR) vulnerability exists in the offer view functionality. Authenticated users can manipulate the offer_id parameter to access offers belonging to other users. The issue is caused by missing authorization checks ensuring that the requested offer belonged to the currently authenticated user. Commit dd082a134a225b8dcd401b6224eead4fb183ea1c contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23843.json
- https://github.com/sibercii6-crypto/teklifolustur_app/security/advisories/GHSA-6h9r-mmg3-cg7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-23843
- https://github.com/sibercii6-crypto/teklifolustur_app/commit/dd082a134a225b8dcd401b6224eead4fb183ea1c
