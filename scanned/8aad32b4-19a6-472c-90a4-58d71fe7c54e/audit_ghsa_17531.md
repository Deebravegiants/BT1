# [H] Salt vulnerable to arbitrary event injection

## Summary
Severity: High
Advisory: GHSA-c46w-gr7f-jm2p
CVE: CVE-2025-22239
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-c46w-gr7f-jm2p
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3006.0rc1 <3006.12
- PyPI: `salt` — affected >=3007.0rc1 <3007.4

## Details
Arbitrary event injection on Salt Master. The master's "_minion_event" method can be used by and authorized minion to send arbitrary events onto the master's event bus.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22239
- https://github.com/saltstack/salt/commit/41d834bf800d86fc496e4fac2d3875fc2aca7c62
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
