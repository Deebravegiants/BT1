# [M] webpki: CRLs not considered authoritative by Distribution Point due to faulty matching logic

## Summary
Severity: Medium
Advisory: GHSA-pwjx-qhcg-rvj4
CWE: CWE-299
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-pwjx-qhcg-rvj4
Type: github-advisory

## Affected
- crates.io: `rustls-webpki` — affected >=0.102.0-alpha.0 <0.103.10
- crates.io: `rustls-webpki` — affected >=0.104.0-alpha.1 <0.104.0-alpha.5

## Details
If a certificate had more than one `distributionPoint`, then only the first `distributionPoint` would be considered against each CRL's `IssuingDistributionPoint` `distributionPoint`, and then the certificate's subsequent `distributionPoint`s would be ignored.

The impact was that correct provided CRLs would not be consulted to check revocation. With `UnknownStatusPolicy::Deny` (the default) this would lead to incorrect but safe `Error::UnknownRevocationStatus`. With `UnknownStatusPolicy::Allow` this would lead to inappropriate acceptance of revoked certificates.

This vulnerability is thought to be of limited impact. This is because both the certificate and CRL are signed -- an attacker would need to compromise a trusted issuing authority to trigger this bug.  An attacker with such capabilities could likely bypass revocation checking through other more impactful means (such as publishing a valid, empty CRL.)

More likely, this bug would be latent in normal use, and an attacker could leverage faulty revocation checking to continue using a revoked credential.

## References
- https://github.com/rustls/webpki/security/advisories/GHSA-pwjx-qhcg-rvj4
- https://github.com/rustls/webpki
- https://rustsec.org/advisories/RUSTSEC-2026-0049.html
