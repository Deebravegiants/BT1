# [M] Vantage6: 2FA can be circumvented with hacked email access

## Summary
Severity: Medium
Advisory: GHSA-4c5c-2vc3-x5w2
CVE: CVE-2024-27928
CWE: CWE-308
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-4c5c-2vc3-x5w2
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <5.0.0

## Details
### Impact
If an attacker hacks into a vantage6 user's email account, they can 1) reset the password via email and then 2) reset the 2FA token via email. This way they reduce 2FA to 1FA (email access). 

Note that most email providers require 2FA to access email, so this issue is not very likely to cause issues.

### Proposed solution

Many web apps do not provide functionality to reset 2FA token (probably for this reason), but provide recovery codes as well. It would be better to provide these recovery codes to the user 1 time and then delete the option to reset it.

An alternative may be to only let server administrators reset 2FA token. However, this has as disadvantage that a hacked email account may send messages to the server admin to reset them, which they may fall for.

### Patches
No

### Workarounds
No

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-4c5c-2vc3-x5w2
- https://github.com/vantage6/vantage6/issues/1932
- https://github.com/vantage6/vantage6
- https://github.com/vantage6/vantage6/blob/main/docs/release_notes.rst#500
