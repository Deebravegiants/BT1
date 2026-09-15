# [M] Boruta dynamic client registration allows creation of over-privileged OAuth clients

## Summary
Severity: Medium
Advisory: CVE-2026-65635
Aliases: EEF-CVE-2026-65635, GHSA-w869-fcf2-68vp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:L/SC:L/SI:L/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-65635
Type: osv

## Details
Improper Isolation or Compartmentalization vulnerability in malach-it boruta (Elixir.Boruta.Openid module) allows attackers to register OpenID Connect clients with administrative privileges through the dynamic client registration entry point. Boruta.Openid.register_client/3 forwards caller-supplied registration parameters to the administrative client creation path without a public/admin field-level allowlist, so an unauthenticated registrant can set security-sensitive attributes including supported grant types, authorized scopes, PKCE enforcement, public refresh and revocation behavior, token lifetimes, and signing settings. The library does not distinguish between metadata a public registrant is allowed to set and administrative controls that should require operator approval.

This vulnerability is associated with program files lib/boruta/openid.ex and program routines 'Elixir.Boruta.Openid':register_client/3, 'Elixir.Boruta.Openid':parse_registration_params/2.

This issue affects boruta from 2.3.0 before 2.3.7.

## References
- https://cna.erlef.org/cves/CVE-2026-65635.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-65635
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65635.json
- https://github.com/malach-it/boruta_auth/security/advisories/GHSA-w869-fcf2-68vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-65635
- https://github.com/malach-it/boruta_auth/commit/82584c854a332482232fd25301ab12a835f9f643
- https://github.com/malach-it/boruta_auth/commit/95619a1beaff68fa766cca9b388e7c780d182525
- https://github.com/malach-it/boruta_auth
