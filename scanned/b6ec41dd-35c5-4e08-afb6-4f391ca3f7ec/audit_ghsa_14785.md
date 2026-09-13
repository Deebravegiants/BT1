# [H] Arbitrary file deletion in litellm

## Summary
Severity: High
Advisory: GHSA-3xr8-qfvj-9p9j
CVE: CVE-2024-4888
CWE: CWE-20, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-3xr8-qfvj-9p9j
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.35.36

## Details
BerriAI's litellm, in its latest version, is vulnerable to arbitrary file deletion due to improper input validation on the `/audio/transcriptions` endpoint. An attacker can exploit this vulnerability by sending a specially crafted request that includes a file path to the server, which then deletes the specified file without proper authorization or validation. This vulnerability is present in the code where `os.remove(file.filename)` is used to delete a file, allowing any user to delete critical files on the server such as SSH keys, SQLite databases, or configuration files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4888
- https://github.com/BerriAI/litellm/pull/3193
- https://github.com/BerriAI/litellm
- https://huntr.com/bounties/48461d89-cf13-4ad3-a43e-0d37da08fc6c
