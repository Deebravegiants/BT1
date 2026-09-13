# [M] Discourse DM limits aren’t always properly enforced

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-32376
Aliases: CVE-2025-32376, GHSA-mqqq-h2x3-46fr
Ecosystem: Bitnami
Published: 2025-05-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-32376
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.3

## Details
Discourse is an open-source discussion platform. Prior to versions 3.4.3 on the stable branch and 3.5.0.beta3 on the beta branch, the users limit for a DM can be bypassed, thus giving the ability to potentially create a DM with every user from a site in it. This issue has been patched in stable version 3.4.3 and beta version 3.5.0.beta3.

## References
- https://github.com/discourse/discourse/commit/21a7f3162221c393f9bb13721451aa7f237d881a
- https://github.com/discourse/discourse/security/advisories/GHSA-mqqq-h2x3-46fr
- https://nvd.nist.gov/vuln/detail/CVE-2025-32376
