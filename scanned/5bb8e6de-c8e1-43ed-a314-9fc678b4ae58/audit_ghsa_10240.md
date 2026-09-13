# [M] October Rain has a Twig Sandbox Bypass via Collection Methods

## Summary
Severity: Medium
Advisory: GHSA-m5qg-jc75-4jp6
CVE: CVE-2026-22692
CWE: CWE-284, CWE-693
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-m5qg-jc75-4jp6
Type: github-advisory

## Affected
- Packagist: `october/rain` — affected >=4.0.0 <4.1.5
- Packagist: `october/rain` — affected >=0 <3.7.13

## Details
A sandbox bypass vulnerability was identified in the optional Twig safe mode feature (`CMS_SAFE_MODE`). Certain methods on the `collect()` helper were not properly restricted, allowing authenticated users with template editing permissions to bypass sandbox protections.

### Impact
- Bypass of Twig sandbox restrictions
- Only affects installations with `CMS_SAFE_MODE` enabled (disabled by default)
- Requires authenticated backend access with CMS template editing permissions

### Patches
The vulnerability has been patched in v4.1.5 and v3.7.13. All users who have enabled safe mode are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Disable `CMS_SAFE_MODE` if untrusted template editing is not required
- Restrict CMS template editing permissions to fully trusted administrators only

### References
- Reported by Łukasz Rybak

## References
- https://github.com/octobercms/october/security/advisories/GHSA-m5qg-jc75-4jp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-22692
- https://github.com/octobercms/october
