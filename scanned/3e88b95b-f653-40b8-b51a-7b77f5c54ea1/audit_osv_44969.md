# [M] MISP OIDC authentication bypass via automatic email-based account linking under insecure IdP configurations

## Summary
Severity: Medium
Advisory: CVE-2026-9084
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-9084
Type: osv

## Details
MISP’s OIDC authentication plugin allowed automatic linking of an OIDC identity to an existing local user account based on the email claim when the local account had no stored sub value. Under insecure or untrusted IdP configurations where email ownership is not enforced, an attacker with a valid OIDC token could assert a victim’s email address and authenticate as that user, leading to account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9084.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9084
- https://github.com/MISP/MISP/commit/71f5662c1b5886613d2cd5c72fd93bb4ca6fa172
