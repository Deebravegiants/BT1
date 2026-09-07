# [M] Copyparty vulnerable to reflected XSS via setck parameter

## Summary
Severity: Medium
Advisory: GHSA-62cr-6wp5-q43h
CVE: CVE-2026-27948
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-62cr-6wp5-q43h
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.20.9

## Details
### Summary
An XSS allows for reflected cross-site scripting via URL-parameter `?setck=...`

### Details
A reflected cross-site scripting (XSS) vulnerability could allow an attacker to execute malicious javascript by tricking users into accessing a malicious link.

The worst-case outcome of this is being able to move or delete existing files on the server, or upload new files, using the account of the person who clicks the malicious link.

### Indicators of Compromise
All attempted attacks (successful or not) would be logged to both the copyparty serverlog and the accesslog of the reverseproxy, and are detected by `grep -E '[?&]setck=[^&"]*%'` (the text `setck=` eventually followed by the `%` character).

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-62cr-6wp5-q43h
- https://nvd.nist.gov/vuln/detail/CVE-2026-27948
- https://github.com/9001/copyparty/commit/31b2801fd041f803f4a3d5c12c7d7cb5419048bc
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.20.9
