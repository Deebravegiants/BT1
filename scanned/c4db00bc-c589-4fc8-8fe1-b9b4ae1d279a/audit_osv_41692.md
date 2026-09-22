# [C] Cross-project instance copy bypasses target project restrictions via TOCTOU in config merge

## Summary
Severity: Critical
Advisory: CVE-2026-63297
Aliases: GHSA-v989-qw7w-xvg4
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63297
Type: osv

## Details
An authorization bypass vulnerability in LXD due to a timing flaw during configuration merging allows an authenticated attacker to bypass target project restrictions during cross-project instance copies. When copying an instance to a target project, LXD performs restriction checks before configuration merging is complete, creating a time-of-check to time-of-use (TOCTOU) condition. An attacker can exploit this flaw to copy instances with disallowed high-privilege configurations into restricted projects, bypassing security controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63297.json
- https://github.com/canonical/lxd/security/advisories/GHSA-v989-qw7w-xvg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-63297
- https://github.com/canonical/lxd
