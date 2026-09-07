# [M] Kiwi TCMS has an Open Redirect via unvalidated next parameter in account confirmation endpoint

## Summary
Severity: Medium
Advisory: GHSA-hmj5-jm8h-h9fh
CVE: CVE-2026-54724
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-hmj5-jm8h-h9fh
Type: github-advisory

## Affected
- PyPI: `kiwitcms` — affected >=0

## Details
### Summary

An open redirect vulnerability in the account confirmation endpoint allows an unauthenticated attacker to craft a URL hosted on a legitimate Kiwi TCMS instance that redirects victims to an arbitrary external domain. The attack surface is particularly relevant for phishing campaigns targeting Kiwi TCMS users, as the malicious link originates from a trusted organizational hostname.

### Impact

This is an open redirect vulnerability (CWE-601). Any unauthenticated attacker can exploit it against any user of a Kiwi TCMS deployment.

The primary risk is phishing. Because Kiwi TCMS is typically deployed as an internal tool for engineering and QA teams, a redirect from the organization's own hostname carries high implicit trust. An attacker can use this endpoint to:
- Redirect victims to a credential-harvesting page styled to match the Kiwi TCMS or corporate SSO login.
- Bypass email security filters and link-reputation checks that allowlist the organization's domain.
- Distribute malware via a convincing "confirm your account" lure.

## References
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-hmj5-jm8h-h9fh
- https://github.com/kiwitcms/Kiwi
- https://github.com/kiwitcms/Kiwi/releases/tag/v16.1
- https://kiwitcms.org/blog/kiwi-tcms-team/2026/06/24/kiwi-tcms-161
