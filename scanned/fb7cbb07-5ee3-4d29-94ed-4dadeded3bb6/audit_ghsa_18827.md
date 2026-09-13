# [M] BBOT's gitlab.py exposes globally configured "gitlab" API key

## Summary
Severity: Medium
Advisory: GHSA-p3v4-c93g-cmhw
CVE: CVE-2025-10282
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-p3v4-c93g-cmhw
Type: github-advisory

## Affected
- PyPI: `bbot` — affected >=0 <2.7.2
- PyPI: `bbot` — affected >=2.7.0.6919rc0 <2.7.2

## Details
### Summary

bbot's `gitlab.py` sends the user's "gitlab" API key to on-premise GitLab instances.

If a user has configured a gitlab.com API key using this mechanism, it may be leaked to an attacker-controlled server.

### Impact

A user with a "gitlab" API key configured who uses bbot to scan a malicious webserver may leak their gitlab.com API key to an untrustworthy server.

## References
- https://github.com/blacklanternsecurity/bbot/security/advisories/GHSA-p3v4-c93g-cmhw
- https://nvd.nist.gov/vuln/detail/CVE-2025-10282
- https://blog.blacklanternsecurity.com/p/bbot-security-advisory-gitdumper
- https://github.com/blacklanternsecurity/bbot
