# [H] ZenML unauthenticated DoS via Multipart Boundry

## Summary
Severity: High
Advisory: GHSA-6gmf-2369-c76c
CVE: CVE-2024-9340
CWE: CWE-400, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-6gmf-2369-c76c
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.68.0

## Details
A Denial of Service (DoS) vulnerability in zenml-io/zenml version 0.66.0 allows unauthenticated attackers to cause excessive resource consumption by sending malformed multipart requests with arbitrary characters appended to the end of multipart boundaries. This flaw in the multipart request boundary processing mechanism leads to an infinite loop, resulting in a complete denial of service for all users. Affected endpoints include `/api/v1/login` and `/api/v1/device_authorization`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9340
- https://github.com/zenml-io/zenml/commit/cba152eb9ca3071c8372b0b91c02d9d3351de48d
- https://github.com/pypa/advisory-database/tree/main/vulns/zenml/PYSEC-2025-57.yaml
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/c9200654-7dc0-4c1d-8573-ab79a87fb4f6
