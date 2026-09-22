# [H] Capgo - Account Merge via Poisoned public.users.email in SSO Provisioning

## Summary
Severity: High
Advisory: CVE-2026-56215
Aliases: GHSA-wqc6-fhwf-qpww
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-20
Source: https://osv.dev/vulnerability/CVE-2026-56215
Type: osv

## Details
Capgo before 12.128.12 allows authenticated users to modify their mutable public.users.email to arbitrary addresses, which the SSO provisioning endpoint trusts as an account-merge key. Attackers can pre-position their account with a victim's corporate SSO email, causing the provision-user endpoint to merge the victim's SSO identity into the attacker-controlled account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56215.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-wqc6-fhwf-qpww
- https://nvd.nist.gov/vuln/detail/CVE-2026-56215
- https://www.vulncheck.com/advisories/capgo-account-merge-via-poisoned-public-users-email-in-sso-provisioning
