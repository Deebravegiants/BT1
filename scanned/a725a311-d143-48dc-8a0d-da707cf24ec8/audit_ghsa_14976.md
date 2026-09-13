# [M] Directory creation by malicious user in saltstack

## Summary
Severity: Medium
Advisory: GHSA-q27c-j6j9-53w3
CVE: CVE-2024-22231
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-q27c-j6j9-53w3
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3005.5
- PyPI: `salt` — affected >=3006.0 <3006.6

## Details
Syndic cache directory creation is vulnerable to a directory traversal attack in salt project which can lead a malicious attacker to create an arbitrary directory on a Salt master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22231
- https://github.com/saltstack/salt/commit/e0cdb80b55123f4a024759ffcf2b3f0e0788e7ab
- https://github.com/saltstack/salt
- https://saltproject.io/security-announcements/2024-01-31-advisory
