# [H] Improper sanitization of target names

## Summary
Severity: High
Advisory: GHSA-x3r5-q6mj-m485
CVE: CVE-2021-41149
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-x3r5-q6mj-m485
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.12.0

## Details
### Impact
The tough library, prior to 0.12.0, does not properly sanitize target names when caching a repository, or when saving specific targets to an output directory. When targets are cached or saved, files could be overwritten with arbitrary content anywhere on the system.

AWS would like to thank https://github.com/jku for reporting this issue.

### Patches
A fix is available in version 0.12.0.

### Workarounds
No workarounds to this issue are known.

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-x3r5-q6mj-m485
- https://nvd.nist.gov/vuln/detail/CVE-2021-41149
- https://github.com/awslabs/tough/commit/1809b9bd1106d78a51fbea3071aa97a3530bac9a
- https://github.com/awslabs/tough
