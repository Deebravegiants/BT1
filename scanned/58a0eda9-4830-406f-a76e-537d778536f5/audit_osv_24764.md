# [M] CVE-2023-26157

## Summary
Severity: Medium
Advisory: CVE-2023-26157
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H/E:P)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-26157
Type: osv

## Details
Versions of the package libredwg before 0.12.5.6384 are vulnerable to Denial of Service (DoS) due to an out-of-bounds read involving section->num_pages in decode_r2007.c.

## References
- https://security.snyk.io/vuln/SNYK-UNMANAGED-LIBREDWG-6070730
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26157.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26157
- https://github.com/LibreDWG/libredwg/issues/850
- https://github.com/LibreDWG/libredwg/commit/c8cf03ce4c2315b146caf582ea061c0460193bcc
