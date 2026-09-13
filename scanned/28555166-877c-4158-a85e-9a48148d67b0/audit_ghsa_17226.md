# [H] libxmljs has segmentation fault, potentially leading to a denial-of-service (DoS)

## Summary
Severity: High
Advisory: GHSA-jv72-59wq-8rxm
CVE: CVE-2025-25341
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-jv72-59wq-8rxm
Type: github-advisory

## Affected
- npm: `libxmljs` — affected >=0

## Details
A vulnerability exists in the libxmljs 1.0.11 when parsing a specially crafted XML document. Accessing the internal _ref property on entity_ref and entity_decl nodes causes a segmentation fault, potentially leading to a denial-of-service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25341
- https://github.com/libxmljs/libxmljs/issues/667
- https://github.com/libxmljs/libxmljs
