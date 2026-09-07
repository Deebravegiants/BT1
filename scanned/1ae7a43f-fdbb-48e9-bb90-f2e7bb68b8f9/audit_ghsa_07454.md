# [M] Weblate SSRF: outbound URL guard misses some private ranges

## Summary
Severity: Medium
Advisory: GHSA-vmfc-9982-2m45
CVE: CVE-2026-50127
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-vmfc-9982-2m45
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=5.15 <2026.6

## Details
### Impact

Weblate's `VCS_RESTRICT_PRIVATE` did not properly account for some transitional IPv6 ranges, multicast addresses, or some semi-private IPv4 ranges, which allowed some addresses to bypass private range restrictions.

### Patches

* https://github.com/WeblateOrg/weblate/pull/19768

### Resources

The issue was reported by @tonghuaroot via GitHub, and the same user also provided the initial patch.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-vmfc-9982-2m45
- https://nvd.nist.gov/vuln/detail/CVE-2026-50127
- https://github.com/WeblateOrg/weblate/pull/19768
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-2026.6
