# [C] @cgauge/yaml npm Package Arbitrary Code Execution via eval() YAML Tag

## Summary
Severity: Critical
Advisory: CVE-2026-76833
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76833
Type: osv

## Details
@cgauge/yaml npm package contains an arbitrary code execution vulnerability that allows attackers to execute arbitrary JavaScript by embedding a custom !js YAML tag whose construct callback unconditionally calls eval() on attacker-supplied string values during document parsing. Any application parsing untrusted YAML input with this library exposes full Node.js runtime authority, including environment variable access, filesystem read/write, network access, and subprocess execution, with no safe-mode alternative or opt-out mechanism available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76833.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76833
- https://www.vulncheck.com/advisories/cgauge-yaml-npm-package-arbitrary-code-execution-via-eval-yaml-tag
- https://github.com/cgauge/packages
- https://gist.github.com/arjunjaincs/35da3a80b4b16f324f194acec18489ba
