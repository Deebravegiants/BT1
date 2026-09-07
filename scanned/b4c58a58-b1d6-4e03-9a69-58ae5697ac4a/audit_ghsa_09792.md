# [C] LoLLMs is vulnerable to Improper Access Control through weak secret key

## Summary
Severity: Critical
Advisory: GHSA-9296-v3fr-j92j
CVE: CVE-2026-1114
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-9296-v3fr-j92j
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <2.2.0

## Details
In parisneo/lollms version 2.1.0, the application's session management is vulnerable to improper access control due to the use of a weak secret key for signing JSON Web Tokens (JWT). This vulnerability allows an attacker to perform an offline brute-force attack to recover the secret key. Once the secret key is obtained, the attacker can forge administrative tokens by modifying the JWT payload and resigning it with the cracked secret. This enables unauthorized users to escalate privileges, impersonate the administrator, and gain access to restricted endpoints. The issue is resolved in version 2.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1114
- https://github.com/parisneo/lollms/commit/a3b2b82b84d537a9da63e63a370a6a8ad55fed34
- https://github.com/parisneo/lollms
- https://github.com/pypa/advisory-database/tree/main/vulns/lollms/PYSEC-2026-170.yaml
- https://huntr.com/bounties/608b2a3b-2225-438e-9e61-ffbfdec2ed89
