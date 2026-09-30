# [C] CVE-2019-9812

## Summary
Severity: Critical
Advisory: CVE-2019-9812
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-9812
Type: osv

## Details
Given a compromised sandboxed content process due to a separate vulnerability, it is possible to escape that sandbox by loading accounts.firefox.com in that process and forcing a log-in to a malicious Firefox Sync account. Preference settings that disable the sandbox are then synchronized to the local machine and the compromised browser would restart without the sandbox if a crash is triggered. This vulnerability affects Firefox ESR < 60.9, Firefox ESR < 68.1, and Firefox < 69.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-25/
- https://www.mozilla.org/security/advisories/mfsa2019-26/
- https://www.mozilla.org/security/advisories/mfsa2019-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1538008
- https://bugzilla.mozilla.org/show_bug.cgi?id=1538015
