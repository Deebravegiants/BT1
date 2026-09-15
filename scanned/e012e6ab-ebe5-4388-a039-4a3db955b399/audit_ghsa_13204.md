# [H] Economizzer host header injection vulnerability

## Summary
Severity: High
Advisory: GHSA-hqp9-mrjw-7qq2
CVE: CVE-2023-38877
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-hqp9-mrjw-7qq2
Type: github-advisory

## Affected
- Packagist: `gugoan/economizzer` — affected >=0

## Details
A host header injection vulnerability exists in gugoan's Economizzer v.0.9-beta1 and commit 3730880 (April 2023). By sending a specially crafted host header in the reset password request, it is possible to send password reset links to users which, once clicked, lead to an attacker-controlled server and thus leak the password reset token. This allows an attacker to reset other users' passwords.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38877
- https://github.com/gugoan/economizzer/commit/37308802dfe00d43df396a8afaa2096ece8b7b57
- https://github.com/dub-flow/vulnerability-research/tree/main/CVE-2023-38877
- https://github.com/gugoan/economizzer
- https://www.economizzer.org
