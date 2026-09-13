# [M] Economizzer user enumeration vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h3qf-v68r-35jg
CVE: CVE-2023-38871
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-h3qf-v68r-35jg
Type: github-advisory

## Affected
- Packagist: `gugoan/economizzer` — affected >=0

## Details
The commit 3730880 (April 2023) and v.0.9-beta1 of gugoan Economizzer has a user enumeration vulnerability in the login and forgot password functionalities. The app reacts differently when a user or email address is valid, and when it's not. This may allow an attacker to determine whether a user or email address is valid, or brute force valid usernames and email addresses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38871
- https://github.com/gugoan/economizzer/commit/37308802dfe00d43df396a8afaa2096ece8b7b57
- https://github.com/dub-flow/vulnerability-research/tree/main/CVE-2023-38871
- https://github.com/gugoan/economizzer
- https://www.economizzer.org
