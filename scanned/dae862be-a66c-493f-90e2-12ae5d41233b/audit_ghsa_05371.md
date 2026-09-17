# [H] Salt Authentication Protocol Version Downgrade Allows Minion Impersonation

## Summary
Severity: High
Advisory: GHSA-vcf3-26xf-fw4m
CVE: CVE-2025-62349
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-vcf3-26xf-fw4m
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3006.12 <3006.17
- PyPI: `salt` — affected >=3007.4 <3007.9

## Details
Salt contains an authentication protocol version downgrade weakness that can allow a malicious minion to bypass newer authentication/security features by using an older request payload format, enabling minion impersonation and circumventing protections introduced in response to prior issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62349
- https://github.com/saltstack/salt/issues/68467
- https://github.com/saltstack/salt/commit/3d5708acae16d039a1e2b5529c8e14a0d3255611
- https://docs.saltproject.io/en/latest/topics/releases/3006.17.html
- https://docs.saltproject.io/en/latest/topics/releases/3007.9.html
- https://github.com/saltstack/salt
