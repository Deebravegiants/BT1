# [H] Mesa: Checking out of untrusted code in `benchmarks.yml` workflow may lead to code execution in privileged runner

## Summary
Severity: High
Advisory: CVE-2026-29075
Aliases: GHSA-3j55-5q6x-2h48
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-29075
Type: osv

## Details
Mesa is an open-source Python library for agent-based modeling, simulating complex systems and exploring emergent behaviors. In version 3.5.0 and prior, checking out of untrusted code in benchmarks.yml workflow may lead to code execution in privileged runner. This issue has been patched via commit c35b8cd.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29075.json
- https://github.com/mesa/mesa/security/advisories/GHSA-3j55-5q6x-2h48
- https://nvd.nist.gov/vuln/detail/CVE-2026-29075
- https://github.com/mesa/mesa/commit/c35b8cd67fc89dd680ae218e49b77f6e1ee07a27
