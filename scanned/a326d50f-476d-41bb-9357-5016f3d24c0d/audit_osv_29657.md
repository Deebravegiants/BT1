# [M] CVE-2024-45191

## Summary
Severity: Medium
Advisory: CVE-2024-45191
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2024-45191
Type: osv

## Details
An issue was discovered in Matrix libolm through 3.2.16. The AES implementation is vulnerable to cache-timing attacks due to use of S-boxes. This is related to software that uses a lookup table for the SubWord step. This refers to the libolm implementation of Olm. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://news.ycombinator.com/item?id=41249371
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45191.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45191
- https://gitlab.matrix.org/matrix-org/olm/-/commit/6d4b5b07887821a95b144091c8497d09d377f985
- https://gitlab.matrix.org/matrix-org/olm/
- https://soatok.blog/2024/08/14/security-issues-in-matrixs-olm-library/
