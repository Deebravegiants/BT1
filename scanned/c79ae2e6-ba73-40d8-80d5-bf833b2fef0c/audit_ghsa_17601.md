# [M] Salt's salt.auth.pki module does not properly authenticate callers

## Summary
Severity: Medium
Advisory: GHSA-4j59-vv55-q6h3
CVE: CVE-2024-38825
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-4j59-vv55-q6h3
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3006.0rc1 <3006.12
- PyPI: `salt` — affected >=3007.0rc1 <3007.4

## Details
The salt.auth.pki module does not properly authenticate callers. The "password" field contains a public certificate which is validated against a CA certificate by the module. This is not pki authentication, as the caller does not need access to the corresponding private key for the authentication attempt to be accepted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38825
- https://github.com/saltstack/salt/commit/5ff18fd0ececdfd083ddce693c3ccef30e44f155
- https://github.com/saltstack/salt/commit/d7cb64e44db5f82fd615373f5dca2eb1fb29bbab
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
