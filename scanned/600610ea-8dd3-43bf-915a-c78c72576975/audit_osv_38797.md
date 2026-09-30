# [H] Improper Input Validation leading to Improper Control of Generation of Code ('Code Injection') in pyp2spec

## Summary
Severity: High
Advisory: CVE-2026-42301
Aliases: GHSA-r35x-v8p8-xvhw, PYSEC-2026-3003
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-09
Source: https://osv.dev/vulnerability/CVE-2026-42301
Type: osv

## Details
pyp2spec generates working Fedora RPM spec file for Python projects. Prior to version 0.14.1, pyp2spec was writing PyPI package metadata (e.g. the summary field) into the generated spec file without escaping RPM macro directives. When a packager then runs rpmbuild, those directives get evaluated, so a malicious package can execute arbitrary commands on the build machine. This issue has been patched in version 0.14.1.

## References
- https://github.com/befeleme/pyp2spec/releases/tag/v0.14.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42301.json
- https://github.com/befeleme/pyp2spec/security/advisories/GHSA-r35x-v8p8-xvhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42301
