# [M] vantage6 vulnerable to a username timing attack on recover password/MFA token

## Summary
Severity: Medium
Advisory: GHSA-5h3x-6gwf-73jm
CVE: CVE-2024-24770
CWE: CWE-208, CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-5h3x-6gwf-73jm
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <4.3.0

## Details
### Impact
Much like https://github.com/vantage6/vantage6/security/advisories/GHSA-45gq-q4xh-cp53, it is possible to find which usernames exist in vantage6 by calling the API routes `/recover/lost` and `/2fa/lost`, which send emails to users if they have lost their password or MFA token. Usernames can be found by assessing response time differences, and additionally, they can be found because the endpoint gives a response "Failed to login" if the username exists.

### Patches
No

### Workarounds
No

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-45gq-q4xh-cp53
- https://github.com/vantage6/vantage6/security/advisories/GHSA-5h3x-6gwf-73jm
- https://nvd.nist.gov/vuln/detail/CVE-2024-24770
- https://github.com/vantage6/vantage6/commit/aecfd6d0e83165a41a60ebd52d2287b0217be26b
- https://github.com/vantage6/vantage6
