# [C] Hugo before v0.165.0 Insufficient Permission Restriction via TailwindCSS

## Summary
Severity: Critical
Advisory: CVE-2026-89259
Aliases: GHSA-vrm6-x8vp-mv2r
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-89259
Type: osv

## Details
Hugo is a static site generator. From v0.161.0, Hugo executes Node tools under Node's permission model, but TailwindCSS — included in the default security.exec.allow list — requires a highly permissive configuration (--allow-addons, --allow-child-process, --allow-worker). As a result, the restrictions intended by the fix for GHSA-x597-9fr4-5857 could still be bypassed, allowing a Node tool invoked during a build to read and write files outside the project's working directory. Affected versions are those after v0.43; the issue was fixed in v0.165.0 by removing tailwindcss from the default security.exec.allow list. Users who do not use TailwindCSS, or who only build trusted sites, are not affected. As a workaround, users can define a restrictive security.exec.allow list in hugo.toml.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89259.json
- https://github.com/gohugoio/hugo/security/advisories/GHSA-vrm6-x8vp-mv2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-89259
- https://www.vulncheck.com/advisories/hugo-before-0.165.0-insufficient-permission-restriction-via-tailwindcss
