# [M] Weblate: Prefix-Based Repository Boundary Check Bypass via Symlink/Junction Path Prefix Collision

## Summary
Severity: Medium
Advisory: GHSA-ffgh-3jrf-8wvh
CVE: CVE-2026-40256
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-ffgh-3jrf-8wvh
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17

## Details
### Impact
Weblate repository-boundary validation relies on string prefix checks on resolved absolute paths. In multiple code paths, the check uses startswith against the repository root path. This is not path-segment aware and can be bypassed when the external path shares the same string prefix as the repository path (for example, repo and repo_outside).

### Patches
* https://github.com/WeblateOrg/weblate/pull/18847

### References
Thanks to [m9nx4u](https://hackerone.com/m9nx4u) for reporting this issue via HackerOne.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-ffgh-3jrf-8wvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-40256
- https://github.com/WeblateOrg/weblate/pull/18847
- https://github.com/WeblateOrg/weblate/commit/e30dbcb33ae78e754ecef192d54f996b89cb4e15
- https://github.com/WeblateOrg/weblate
