# [H] Economizzer remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-pq98-6hf6-3rj3
CVE: CVE-2023-38874
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-pq98-6hf6-3rj3
Type: github-advisory

## Affected
- Packagist: `gugoan/economizzer` — affected >=0

## Details
A remote code execution (RCE) vulnerability via an insecure file upload exists in gugoan's Economizzer v.0.9-beta1 and commit 3730880 (April 2023). A malicious attacker can upload a PHP web shell as an attachment when adding a new cash book entry. Afterwards, the attacker may visit the web shell and execute arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38874
- https://github.com/gugoan/economizzer/commit/37308802dfe00d43df396a8afaa2096ece8b7b57
- https://github.com/dub-flow/vulnerability-research/tree/main/CVE-2023-38874
- https://github.com/gugoan/economizzer
- https://www.economizzer.org
