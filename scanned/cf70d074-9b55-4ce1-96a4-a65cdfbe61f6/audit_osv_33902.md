# [C] Registrator.jl Argument Injection Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-52480
Aliases: GHSA-w8jv-rg3h-fc68, JLSEC-2025-4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-52480
Type: osv

## Details
Registrator is a GitHub app that automates creation of registration pull requests for julia packages to the General registry. Prior to version 1.9.5, if the clone URL returned by GitHub is malicious (or can be injected using upstream vulnerabilities), an argument injection is possible in the `gettreesha()` function. This can then lead to a potential remote code execution. Users should upgrade immediately to v1.9.5 to receive a patch. All prior versions are vulnerable. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52480.json
- https://github.com/JuliaRegistries/Registrator.jl/security/advisories/GHSA-w8jv-rg3h-fc68
- https://nvd.nist.gov/vuln/detail/CVE-2025-52480
- https://github.com/JuliaRegistries/Registrator.jl/pull/449
