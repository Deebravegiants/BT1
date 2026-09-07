# [M] MobSF vulnerable to Open Redirect in Login Redirect

## Summary
Severity: Medium
Advisory: GHSA-8m9j-2f32-2vx4
CVE: CVE-2024-41955
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-8m9j-2f32-2vx4
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.0.5

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

An open redirect vulnerability exist in MobSF authentication view. 

PoC
1. Go to http://127.0.0.1:8000/login/?next=//afine.com in a web browser.
2. Enter credentials and press "Sign In".
3. You will be redirected to [afine.com](http://afine.com/)

Users who are not using authentication are not impacted.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Update to MobSF v4.0.5

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Disable Authentication

### References
_Are there any links users can visit to find out more?_
Fix: https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/fdaad81314f393d324c1ede79627e9d47986c8c8

### Reporter
Marcin Węgłowski (AFINE Team)

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-8m9j-2f32-2vx4
- https://nvd.nist.gov/vuln/detail/CVE-2024-41955
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/fdaad81314f393d324c1ede79627e9d47986c8c8
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
