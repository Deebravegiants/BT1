# [M] OroCalendarBundle has incorrect system calendar events visibility

## Summary
Severity: Medium
Advisory: GHSA-x2xm-p6vq-482g
CVE: CVE-2023-32062
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-x2xm-p6vq-482g
Type: github-advisory

## Affected
- Packagist: `oro/calendar-bundle` — affected >=4.2.0
- Packagist: `oro/calendar-bundle` — affected >=5.0.0 <5.0.7
- Packagist: `oro/calendar-bundle` — affected >=5.1.0 <5.1.1

## Details
OroPlatform is a package that assist system and user calendar management. Back-office users can access information from any system calendar event, bypassing ACL security restrictions due to insufficient security checks.

## References
- https://github.com/oroinc/crm/security/advisories/GHSA-x2xm-p6vq-482g
- https://nvd.nist.gov/vuln/detail/CVE-2023-32062
- https://github.com/oroinc/OroCalendarBundle/commit/460a8ffb63b10c76f2fa26d53512164851c4909b
- https://github.com/oroinc/OroCalendarBundle/commit/5f4734aa02088191c1c1d90ac0909f48610fe531
- https://github.com/oroinc/crm
