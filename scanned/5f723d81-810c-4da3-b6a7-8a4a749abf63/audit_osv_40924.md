# [H] Capgo - Account Takeover via Cross-Domain SSO Email Assertion in provision-user

## Summary
Severity: High
Advisory: CVE-2026-56223
Aliases: GHSA-jhjh-vp9p-54fg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56223
Type: osv

## Details
Capgo before 12.128.2 contains a cross-domain SSO account takeover vulnerability in the provision-user endpoint that allows attackers to merge arbitrary victim accounts based on email match without validating SSO provider domain authorization. An attacker with enterprise org admin access and a malicious IdP can forge SAML assertions containing victim email addresses to trigger account merge and gain full access to victim accounts, organizations, and data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56223.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-jhjh-vp9p-54fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-56223
- https://www.vulncheck.com/advisories/capgo-account-takeover-via-cross-domain-sso-email-assertion-in-provision-user
