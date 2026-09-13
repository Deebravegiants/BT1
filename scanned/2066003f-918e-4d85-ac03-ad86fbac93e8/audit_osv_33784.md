# [M] GitForge.jl lacks validation for user provided fields

## Summary
Severity: Medium
Advisory: CVE-2025-50178
Aliases: GHSA-g2xx-229f-3qjm, JLSEC-2025-3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-50178
Type: osv

## Details
GitForge.jl is a unified interface for interacting with Git "forges." Versions prior to 0.4.3 lack input validation for user provided values in certain functions. In the `GitForge.get_repo` function for GitHub, the user can provide any string for the owner and repo fields. These inputs are not validated or safely encoded and are sent directly to the server. This means a user can add path traversal patterns like `../` in the input to access any other endpoints on api.github.com that were not intended. Version 0.4.3 contains a patch for the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50178.json
- https://github.com/JuliaWeb/GitForge.jl/security/advisories/GHSA-g2xx-229f-3qjm
- https://nvd.nist.gov/vuln/detail/CVE-2025-50178
- https://github.com/JuliaWeb/GitForge.jl/pull/50
