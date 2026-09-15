# [M] Mobile Security Framework (MobSF) vulnerable to SSRF in firebase database check

## Summary
Severity: Medium
Advisory: GHSA-wpff-wm84-x5cx
CVE: CVE-2024-31215
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-wpff-wm84-x5cx
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <3.9.8

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
SSRF vulnerability in firebase database check logic. The attacker can cause the server to make a connection to internal-only services within the organization’s infrastructure. When malicious app is uploaded to Static analyzer, it is possible to make internal requests.

Credits:  Oleg Surnin (Positive Technologies).

### Patches
_Has the problem been patched? What versions should users upgrade to?_
v3.9.8 and above

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Code level patch

### References
_Are there any links users can visit to find out more?_
https://github.com/MobSF/Mobile-Security-Framework-MobSF/pull/2373

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-wpff-wm84-x5cx
- https://nvd.nist.gov/vuln/detail/CVE-2024-31215
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/pull/2373
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/43bb71d115d78c03faa82d75445dd908e9b32716
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
