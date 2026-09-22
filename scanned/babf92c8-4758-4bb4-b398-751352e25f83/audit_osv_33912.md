# [M] GitHub.jl lacks validation for user-provided fields

## Summary
Severity: Medium
Advisory: CVE-2025-52569
Aliases: GHSA-jg9p-c3wh-q83x, JLSEC-2025-5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-52569
Type: osv

## Details
GitForge.jl is a unified interface for interacting with Git "forges." Versions prior to 5.9.1 lack input validation of input validation for user-provided values in certain functions. In the `GitHub.repo()` function, the user can provide any string for the `repo_name` field. These inputs are not validated or safely encoded and are sent directly to the server. This means a user can add path traversal patterns like `../` in the input to access any other endpoints on `api.github.com` that were not intended. Users should upgrade immediately to v5.9.1 or later to receive a patch. All prior versions are vulnerable. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52569.json
- https://github.com/JuliaWeb/GitHub.jl/security/advisories/GHSA-jg9p-c3wh-q83x
- https://nvd.nist.gov/vuln/detail/CVE-2025-52569
- https://github.com/JuliaWeb/GitHub.jl/pull/224
