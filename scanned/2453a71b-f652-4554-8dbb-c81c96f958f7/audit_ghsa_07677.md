# [M] Weblate: Missing access control for the AddonViewSet API exposes all addon configurations

## Summary
Severity: Medium
Advisory: GHSA-wppc-7cq7-cgfv
CVE: CVE-2026-27457
CWE: CWE-200, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-wppc-7cq7-cgfv
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.16.1

## Details
### Impact

Users were able to obtain add-on configuration via API.

### Patches

* https://github.com/WeblateOrg/weblate/pull/18107
* https://github.com/WeblateOrg/weblate/pull/18164


### References

Weblate thanks @lighthousekeeper1212 for responsible disclosure.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-wppc-7cq7-cgfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-27457
- https://github.com/WeblateOrg/weblate/pull/18107
- https://github.com/WeblateOrg/weblate/pull/18164
- https://github.com/WeblateOrg/weblate/commit/3f58f9a4152bc0cbdd6eff5954f9c7bc4d9f0af9
- https://github.com/WeblateOrg/weblate/commit/7802c9b121eb407c48d4adddd4f2458fb3efef0f
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.16.1
