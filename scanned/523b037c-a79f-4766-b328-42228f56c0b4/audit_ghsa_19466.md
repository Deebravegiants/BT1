# [H] Apollo Compiler Named Fragment Processing Vulnerability

## Summary
Severity: High
Advisory: GHSA-7mpv-9xg6-5r79
CVE: CVE-2025-31496
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-7mpv-9xg6-5r79
Type: github-advisory

## Affected
- crates.io: `apollo-compiler` — affected >=0 <1.27.0

## Details
# Impact

## Summary

A vulnerability in Apollo Compiler allowed queries with deeply nested and reused named fragments to be prohibitively expensive to validate. This could lead to excessive resource consumption and denial of service in applications.

## Details

Named fragments were being processed once per fragment spread in some cases during query validation, leading to exponential resource usage when deeply nested and reused fragments were involved.

## Fix/Mitigation

The validation logic has been updated to process each named fragment only once, preventing redundant traversal.

# Patches
This has been remediated in `apollo-compiler` version 1.27.0.

# Workarounds
No known direct workarounds exist.

## Acknowledgements
We appreciate the efforts of the security community in identifying and improving the performance and security of query validation mechanisms.

## References
- https://github.com/apollographql/apollo-rs/security/advisories/GHSA-7mpv-9xg6-5r79
- https://nvd.nist.gov/vuln/detail/CVE-2025-31496
- https://github.com/apollographql/apollo-rs/pull/952
- https://github.com/apollographql/apollo-rs
