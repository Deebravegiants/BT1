# [H] Weblate: Arbitrary File Read via Symlink

## Summary
Severity: High
Advisory: GHSA-hv99-mxm5-q397
CVE: CVE-2026-34242
CWE: CWE-200, CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-hv99-mxm5-q397
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17

## Details
### Impact

The ZIP download feature didn't verify downloaded file and it could follow symlinks outside the repository.

### Patches

* https://github.com/WeblateOrg/weblate/pull/18683

### References

Thanks to @DavidCarliez for reporting this vulnerability via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-hv99-mxm5-q397
- https://nvd.nist.gov/vuln/detail/CVE-2026-34242
- https://github.com/WeblateOrg/weblate/commit/5db3a2a2e047ecaab627a8731cd744a30b2f51d3
- https://github.com/WeblateOrg/weblate
