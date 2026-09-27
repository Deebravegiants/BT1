# [M] Leaking of user information on Cross-Domain communication in sysend

## Summary
Severity: Medium
Advisory: GHSA-4vvg-x86p-mvqc
CVE: CVE-2022-24762
CWE: CWE-200, CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-4vvg-x86p-mvqc
Type: github-advisory

## Affected
- npm: `sysend` — affected >=0 <1.10.0

## Details
### Impact
Users that use Cross-Origin communication and send sensitive information make it possible for this data to be intercepted.
This is not a big impact because it happens only on the same browser.

### Patches
It has been patched in version 1.10.0

### Workarounds
The only workaround is to not send sensitive information with sysend messages.

## References
- https://github.com/jcubic/sysend.js/security/advisories/GHSA-4vvg-x86p-mvqc
- https://nvd.nist.gov/vuln/detail/CVE-2022-24762
- https://github.com/jcubic/sysend.js/issues/33
- https://github.com/jcubic/sysend.js/commit/a24f4b776fb18191ae0f7e3d90c2c7bec459431a
- https://github.com/jcubic/sysend.js
- https://github.com/jcubic/sysend.js/releases/tag/1.10.0
