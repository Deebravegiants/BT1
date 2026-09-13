# [M] Weblate lacks rate limiting when verifying second factor

## Summary
Severity: Medium
Advisory: GHSA-57jg-m997-cx3q
CVE: CVE-2025-47951
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-57jg-m997-cx3q
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.12

## Details
### Impact

The verification of the second factor was not subject to rate limiting. The absence of rate limiting on the second factor endpoint allows an attacker with valid credentials to automate OTP guessing. 

### Patches

This issue has been addressed in Weblate 5.12 via https://github.com/WeblateOrg/weblate/pull/14918.

### References

Thanks to [obscuredeer](https://hackerone.com/obscuredeer) for reporting this [issue at HackerOne](https://hackerone.com/reports/3150564).

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-57jg-m997-cx3q
- https://nvd.nist.gov/vuln/detail/CVE-2025-47951
- https://github.com/WeblateOrg/weblate/pull/14918
- https://github.com/WeblateOrg/weblate/commit/f806293451248c5d95e45b3b507e9d158bc4f384
- https://hackerone.com/reports/3150564
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.12.1
