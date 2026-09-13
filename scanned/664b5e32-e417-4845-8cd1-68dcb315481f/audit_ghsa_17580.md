# [M] Salt vulnerable to directory traversal attack in minion file cache creation

## Summary
Severity: Medium
Advisory: GHSA-r546-h3ff-q585
CVE: CVE-2025-22238
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-r546-h3ff-q585
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3006.0rc1 <3006.12
- PyPI: `salt` — affected >=3007.0rc1 <3007.4

## Details
Directory traversal attack in minion file cache creation. The master's default cache is vulnerable to a directory traversal attack. Which could be leveraged to write or overwrite 'cache' files outside of the cache directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22238
- https://github.com/saltstack/salt/commit/4b30218edf1a979855ea191d72b30c89f4a5a582
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
