# [C] isolated-vm has vulnerable CachedDataOptions in API

## Summary
Severity: Critical
Advisory: GHSA-2jjq-x548-rhpv
CVE: CVE-2022-39266
CWE: CWE-20, CWE-287, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-2jjq-x548-rhpv
Type: github-advisory

## Affected
- npm: `isolated-vm` — affected >=0 <4.3.7

## Details
### Impact
If the untrusted v8 cached data is passed to the API through CachedDataOptions, the attackers can bypass the sandbox and run arbitrary code in the nodejs process. Version 4.3.7 changes the documentation to warn users that they should not accept `cachedData` payloads from a user.

## References
- https://github.com/laverdet/isolated-vm/security/advisories/GHSA-2jjq-x548-rhpv
- https://nvd.nist.gov/vuln/detail/CVE-2022-39266
- https://github.com/laverdet/isolated-vm/issues/379
- https://github.com/laverdet/isolated-vm/commit/218e87a6d4e8cb818bea76d1ab30cd0be51920e8
- https://github.com/laverdet/isolated-vm
- https://github.com/laverdet/isolated-vm/commits/v4.3.7
