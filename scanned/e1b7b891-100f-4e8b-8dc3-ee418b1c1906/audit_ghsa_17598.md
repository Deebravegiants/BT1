# [M] SignXML's signature verification with HMAC is vulnerable to an algorithm confusion attack

## Summary
Severity: Medium
Advisory: GHSA-6vx8-pcwv-xhf4
CVE: CVE-2025-48994
CWE: CWE-303
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-6vx8-pcwv-xhf4
Type: github-advisory

## Affected
- PyPI: `signxml` — affected >=0 <4.0.4

## Details
When verifying signatures with X509 certificate validation turned off and HMAC shared secret set (`signxml.XMLVerifier.verify(require_x509=False, hmac_key=...`), prior versions of SignXML are vulnerable to a potential algorithm confusion attack. Unless the user explicitly limits the expected signature algorithms using the `signxml.XMLVerifier.verify(expect_config=...)` setting, an attacker may supply a signature unexpectedly signed with a key other than the provided HMAC key, using a different (asymmetric key) signature algorithm.

Starting with signxml 4.0.4, specifying `hmac_key` causes the set of accepted signature algorithms to be restricted to HMAC only, if not already restricted by the user.

## References
- https://github.com/XML-Security/signxml/security/advisories/GHSA-6vx8-pcwv-xhf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-48994
- https://github.com/XML-Security/signxml/commit/e3c0c2b82a3329a65d917830657649c98b8c7600
- https://github.com/XML-Security/signxml
