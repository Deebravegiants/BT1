# [H] Incorrect sanitisation function leads to `XSS` in mermaid

## Summary
Severity: High
Advisory: GHSA-p3rp-vmj9-gv6v
CVE: CVE-2021-43861
CWE: CWE-20, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-p3rp-vmj9-gv6v
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=0 <8.13.8

## Details
### Impact
Malicious diagrams can contain javascript code that can be run at diagram readers machines.

### Patches
The users should upgrade to version 8.13.8

### Workarounds
You need to upgrade in order to avoid this issue.

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-p3rp-vmj9-gv6v
- https://nvd.nist.gov/vuln/detail/CVE-2021-43861
- https://github.com/mermaid-js/mermaid/commit/066b7a0d0bda274d94a2f2d21e4323dab5776d83
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/8.13.8
