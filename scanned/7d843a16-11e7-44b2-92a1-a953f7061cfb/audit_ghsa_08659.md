# [C] phpVMS has an /importer authorization bypass causing full database wipe

## Summary
Severity: Critical
Advisory: GHSA-fv26-4939-62fh
CVE: CVE-2026-42569
CWE: CWE-284, CWE-306, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-fv26-4939-62fh
Type: github-advisory

## Affected
- Packagist: `nabeel/phpvms` — affected >=0 <7.0.6

## Details
# Security Advisory: Unauthenticated Access to Legacy Import Feature

**Severity:** Critical
**Affected versions:** phpVMS 7.x (up to 7.0.5)
**Fixed in:** v7.0.6
**Component:** Legacy importer

## Summary

A critical vulnerability in phpVMS 7.x allowed unauthenticated access to a legacy import feature. Although this feature is deprecated, parts of it remained accessible and operational.

## Impact

A remote attacker could trigger internal processes that modify or delete application data, potentially resulting in:

- Data loss
- Service disruption

No authentication was required.

## Remediation

- **Update immediately** to [the latest patched version](https://github.com/phpvms/phpvms/releases/tag/7.0.7)
- If unable to update:
  - The release link has instructions on how to fix it (it's a one-line fix to comment out the routes)

## Affected Versions

* Affected: phpVMS 7.x ≤ 7.0.5
* Not affected: phpVMS >= 7.0.6, v8 (feature removed from public access)

## References
- https://github.com/phpvms/phpvms/security/advisories/GHSA-fv26-4939-62fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42569
- https://github.com/phpvms/phpvms/commit/f59ba8e0e8fc25c60c3faf14e526cfd49df3f7dc
- https://github.com/phpvms/phpvms
- https://github.com/phpvms/phpvms/releases/tag/7.0.6
- https://github.com/phpvms/phpvms/releases/tag/7.0.7
