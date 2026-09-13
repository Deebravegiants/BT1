# [H] Lord of Large Language Models vulnerable to Observable Discrepancy attack via authenticate_user function

## Summary
Severity: High
Advisory: GHSA-j5pr-vrjj-9v4h
CVE: CVE-2025-6386
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-j5pr-vrjj-9v4h
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0

## Details
The parisneo/lollms repository is affected by a timing attack vulnerability in the `authenticate_user` function within the `lollms_authentication.py` file. This vulnerability allows attackers to enumerate valid usernames and guess passwords incrementally by analyzing response time differences. The affected version is the latest, and the issue is resolved in commit f78437f. The vulnerability arises from the use of Python's default string equality operator for password comparison, which compares characters sequentially and exits on the first mismatch, leading to variable response times based on the number of matching initial characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6386
- https://github.com/parisneo/lollms/commit/f78437f7b5aa39a78c6201912faf4e0645a38c48
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/6da05485-d219-4f18-9ffc-991053524b67
