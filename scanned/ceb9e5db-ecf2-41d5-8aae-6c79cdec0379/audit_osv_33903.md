# [C] Registrator.jl Vulnerable to Argument Injection and Command Injection

## Summary
Severity: Critical
Advisory: CVE-2025-52483
Aliases: GHSA-589r-g8hf-xx59, JLSEC-2025-2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-52483
Type: osv

## Details
Registrator is a GitHub app that automates creation of registration pull requests for julia packages to the General registry. Prior to version 1.9.5, if the clone URL returned by GitHub is malicious (or can be injected using upstream vulnerabilities) a shell script injection can occur within the `withpasswd` function. Alternatively, an argument injection is possible in the `gettreesha `function. either of these can then lead to a potential RCE. Users should upgrade immediately to v1.9.5 to receive a fix. All prior versions are vulnerable. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52483.json
- https://github.com/JuliaRegistries/Registrator.jl/security/advisories/GHSA-589r-g8hf-xx59
- https://nvd.nist.gov/vuln/detail/CVE-2025-52483
- https://github.com/JuliaRegistries/Registrator.jl/pull/448
