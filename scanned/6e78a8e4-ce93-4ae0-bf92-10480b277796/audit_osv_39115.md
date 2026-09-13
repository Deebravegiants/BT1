# [H] e107: Host Header Injection in e107 password reset enables phishing

## Summary
Severity: High
Advisory: CVE-2026-43935
Aliases: GHSA-7pmw-jwvr-cq2x
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-43935
Type: osv

## Details
e107 is a content management system (CMS). Prior to 2.3.4, a Host Header Injection vulnerability in the password reset page allows attackers to manipulate the Host header to generate password reset links pointing to attacker-controlled domains. This can lead to phishing attacks, account takeover, or other security risks. The severity is high, as the vulnerability affects a critical function related to user authentication. This vulnerability is fixed in 2.3.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43935.json
- https://github.com/e107inc/e107/security/advisories/GHSA-7pmw-jwvr-cq2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-43935
- https://github.com/e107inc/e107/commit/04511f9f1d6e97c31ba7cc5bf7f1f9a19d221db6
- https://github.com/e107inc/e107/commit/b0dee8234e273debbf7a8ae054de464f1008f357
- https://github.com/e107inc/e107/commit/c4f9f71b0fd695545d0f09e2277b6f70ff4660fc
