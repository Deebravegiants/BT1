# [M] OpenEXR: OpenEXRCore exr_attr_set_bytes() accepts NULL type_hint with positive hint_length

## Summary
Severity: Medium
Advisory: CVE-2026-55371
Aliases: GHSA-xx72-f24p-cf6r
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-55371
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR high-dynamic-range image file format, widely used in the motion picture industry. Versions 3.4.0 through 3.4.12 contain a NULL pointer dereference in the OpenEXRCore function exr_attr_set_bytes(). The public setter validates the top-level exr_attr_bytes_t value pointer but does not verify that the nested type_hint pointer is non-NULL when hint_length is greater than zero. When a caller supplies a positive hint_length together with a NULL type_hint, exr_attr_bytes_create() allocates a destination type-hint buffer and then copies from the NULL source pointer, causing a deterministic crash. The flaw is reachable through the public OpenEXRCore C API and results in a denial of service. The issue is fixed in version 3.4.13.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-xx72-f24p-cf6r
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55371
