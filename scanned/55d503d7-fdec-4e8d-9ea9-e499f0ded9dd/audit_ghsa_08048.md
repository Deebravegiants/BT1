# [H] rPGP vulnerable to parser crash on crafted RSA secret key packets through CVE-2026-21895

## Summary
Severity: High
Advisory: GHSA-7587-4wv6-m68m
CWE: CWE-703
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-7587-4wv6-m68m
Type: github-advisory

## Affected
- crates.io: `pgp` — affected >=0.16.0-alpha.0 <0.19.0

## Details
### Summary
It was possible to trigger an unhandled edge case in the Rust Crypto rsa crate through rPGP packet parsing functionality, and crash the process that runs rPGP. This problem has been patched in a new rsa version. The new release of rPGP ensures a patched version of the rsa crate is in use, which prevents this issue.

### Details
While parsing a special RSA secret key packet, rPGP calls the rsa crate with the provided key. On vulnerable versions, this results in a Rust "panic" during key construction. Note that an attacker can trigger this situation even in places where applications don't expect to handle foreign key material, for example while attempting to receive a message.

For more information on the rsa crate vulnerability, see https://github.com/RustCrypto/RSA/security/advisories/GHSA-9c48-w39g-hm26 and https://github.com/RustCrypto/RSA/pull/624.
In rPGP, this has been fixed via https://github.com/rpgp/rpgp/pull/698.

### Impact
This issue impacts availability (i.e. applications can crash).

Affected rPGP versions: rPGP 0.16.0-alpha.0 to 0.18.0
Vulnerable rsa versions: all before version 0.9.10

### Workaround
The issue depends on the combination of affected rPGP and rsa versions. Users of affected rPGP versions can pin the patched rsa 0.9.10 via a cargo lockfile to mitigate the issue.

### Attribution
Discovered by Christian Reitter from Radically Open Security during a security review for Proton AG.

## References
- https://github.com/rpgp/rpgp/security/advisories/GHSA-7587-4wv6-m68m
- https://github.com/rpgp/rpgp/pull/698
- https://github.com/rpgp/rpgp/commit/38efa49ce18b3821649de9cd8dea88a959b833a5
- https://github.com/rpgp/rpgp
