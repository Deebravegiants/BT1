# [M] Hugo's Node tool execution allows file system access outside the project directory

## Summary
Severity: Medium
Advisory: GHSA-x597-9fr4-5857
CVE: CVE-2026-44301
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-x597-9fr4-5857
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.43.0 <0.161.0

## Details
## Impact 
When building a Hugo site that uses Node-based asset pipelines (PostCSS, Babel, TailwindCSS), Hugo invoked the configured Node tools without restrictions on file system access. As a result, executing hugo against an untrusted site could allow code running through these tools to read or write files outside the project's working directory.

Users who do not use PostCSS, Babel, or TailwindCSS, or who only build trusted sites, are not affected.

## Patches
From `v0.161.0`, Hugo runs Node tools under Node's permission model with strict defaults: No write access and only read access to the site source directories and files.

## Workarounds
Block these tools in [security.exec.allow](https://gohugo.io/configuration/security/).

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-x597-9fr4-5857
- https://nvd.nist.gov/vuln/detail/CVE-2026-44301
- https://github.com/gohugoio/hugo
