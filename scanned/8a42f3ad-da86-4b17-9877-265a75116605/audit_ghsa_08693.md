# [M] Steamworks game clients/servers using P2P authentication vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-g588-cjg3-6g78
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-g588-cjg3-6g78
Type: github-advisory

## Affected
- crates.io: `steamworks` — affected >=0 <0.13.1

## Details
Processing the raw `ValidateAuthTicketResponse_t` callback data panics when the `m_eAuthSessionResponse` field is `k_EAuthSessionResponseAuthTicketNetworkIdentityFailure`. This can lead to denial of service in game clients and servers using the `begin_authentication_session` API to authenticate players if a malicious game client sends an authentication ticket with a network identity that does not match that of the verifier.

## References
- https://github.com/Noxime/steamworks-rs/issues/321
- https://github.com/Noxime/steamworks-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0121.html
