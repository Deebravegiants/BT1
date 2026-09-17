# [H] Audiobookshelf vulnerable to OIDC token exfiltration and account takeover

## Summary
Severity: High
Advisory: CVE-2025-57800
Aliases: GHSA-vpc2-w73p-39px
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-57800
Type: osv

## Details
Audiobookshelf is an open-source self-hosted audiobook server. In versions 2.6.0 through 2.26.3, the application does not properly restrict redirect callback URLs during OIDC authentication. An attacker can craft a login link that causes Audiobookshelf to store an arbitrary callback in a cookie, which is later used to redirect the user after authentication. The server then issues a 302 redirect to the attacker-controlled URL, appending sensitive OIDC tokens as query parameters. This allows an attacker to obtain the victim's tokens and perform full account takeover, including creating persistent admin users if the victim is an administrator. Tokens are further leaked via browser history, Referer headers, and server logs. This vulnerability impacts all Audiobookshelf deployments using OIDC; no IdP misconfiguration is required. The issue is fixed in version 2.28.0. No known workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57800.json
- https://github.com/advplyr/audiobookshelf/security/advisories/GHSA-vpc2-w73p-39px
- https://nvd.nist.gov/vuln/detail/CVE-2025-57800
- https://github.com/advplyr/audiobookshelf/commit/99a3867ce934b797e21e6ba5390d4b679e35f7cb
