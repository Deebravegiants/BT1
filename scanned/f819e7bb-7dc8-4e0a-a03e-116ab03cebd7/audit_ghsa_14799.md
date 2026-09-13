# [H] lollms vulnerable to dot-dot-slash path traversal in XTTS server

## Summary
Severity: High
Advisory: GHSA-w9qf-83jg-2x6c
CVE: CVE-2024-6139
CWE: CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-w9qf-83jg-2x6c
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0

## Details
A path traversal vulnerability exists in the XTTS server of the parisneo/lollms package version v9.6. This vulnerability allows an attacker to write audio files to arbitrary locations on the system and enumerate file paths. The issue arises from improper validation of user-provided file paths in the `tts_to_file` endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6139
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/fd00f112-efd0-40a1-8227-d6733716e4c0
