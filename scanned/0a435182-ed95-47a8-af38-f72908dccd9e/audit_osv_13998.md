# [C] CVE-2018-6331

## Summary
Severity: Critical
Advisory: CVE-2018-6331
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6331
Type: osv

## Details
Buck parser-cache command loads/saves state using Java serialized object. If the state information is maliciously crafted, deserializing it could lead to code execution. This issue affects Buck versions prior to v2018.06.25.01.

## References
- https://github.com/facebook/buck/commit/8c5500981812564877bd122c0f8fab48d3528ddf
