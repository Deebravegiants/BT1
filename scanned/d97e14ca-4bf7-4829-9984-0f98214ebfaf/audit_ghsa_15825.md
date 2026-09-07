# [H] Permissive Regular Expression in tacquito

## Summary
Severity: High
Advisory: GHSA-p5wf-cmr4-xrwr
CWE: CWE-1333
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2024-10-18
Source: https://github.com/advisories/GHSA-p5wf-cmr4-xrwr
Type: github-advisory

## Affected
- Go: `github.com/facebookincubator/tacquito` — affected >=0 <0.0.0-20241011192817-07b49d1358e6

## Details
### Impact
The CVE is for a software vulnerability. Network admins who have deployed tacquito (or versions of tacquito) in their production environments and use tacquito to perform command authorization for network devices should be impacted.

Tacquito code prior to commit 07b49d1358e6ec0b5aa482fcd284f509191119e2 was performing regex matches on authorized commands and arguments in a more permissive than intended manner. Configured allowed commands/arguments were intended to require a match on the entire string, but instead only enforced a match on a sub-string. This behaviour could potentially allowed unauthorized commands to be executed.

### Patches
The problem has been patched, and users should update to the latest github repo commit to get the patch. 

### Workarounds
Users should be able to add boundary conditions anchors '^' and '$' to their command configs to remediate the vulnerability without the upgrade

## References
- https://github.com/facebookincubator/tacquito/security/advisories/GHSA-p5wf-cmr4-xrwr
- https://nvd.nist.gov/vuln/detail/CVE-2024-49400
- https://github.com/facebookincubator/tacquito/commit/07b49d1358e6ec0b5aa482fcd284f509191119e2
- https://github.com/facebookincubator/tacquito
- https://www.facebook.com/security/advisories/cve-2024-49400
