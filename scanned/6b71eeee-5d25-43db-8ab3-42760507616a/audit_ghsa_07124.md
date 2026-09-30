# [M] Apple App Store Server Python Library: SignedDataVerifier accepts stale OCSP GOOD responses and can bypass certificate revocation checks

## Summary
Severity: Medium
Advisory: GHSA-8f6j-263m-g72x
CWE: CWE-295, CWE-299
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-8f6j-263m-g72x
Type: github-advisory

## Affected
- PyPI: `app-store-server-library` — affected >=0.2.0 <3.1.2

## Details
### Summary
`SignedDataVerifier` attempts to perform online revocation checking when `enable_online_checks=True`, but its OCSP validation logic accepts stale `GOOD` responses as valid indefinitely. In `appstoreserverlibrary/signed_data_verifier.py`, `_ChainVerifier.check_ocsp_status()` verifies the OCSP response signature and CertID match, but never validates the freshness window carried by `producedAt`, `thisUpdate`, or `nextUpdate`.

As a result, a previously valid signed OCSP `GOOD` response can be replayed after it is expired, and the library will still treat the certificate as good. If an App Store signing certificate or intermediate is ever revoked, applications using this library with online checks enabled can continue accepting JWS objects signed with the revoked key as long as a stale signed OCSP response is replayed.

## References
- https://github.com/apple/app-store-server-library-python/security/advisories/GHSA-8f6j-263m-g72x
- https://github.com/apple/app-store-server-library-python
