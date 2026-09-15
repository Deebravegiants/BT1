# [H] cggmp24 and cggmp21 are vulnerable to signature forgery through altered presignatures

## Summary
Severity: High
Advisory: GHSA-8frv-q972-9rq5
CVE: CVE-2025-66017
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-8frv-q972-9rq5
Type: github-advisory

## Affected
- crates.io: `cggmp21` — affected >=0
- crates.io: `cggmp24` — affected >=0 <0.7.0-alpha.2

## Details
### Impact
This attack is against presignatures used in very specific context:
* Presignatures + HD wallets derivation: security level reduces to 85 bits \
  Previously users could generate a presignature, and then choose a HD derivation path while issuing a partial signature via [`Presignature::set_derivation_path`](https://docs.rs/cggmp21/0.6.3/cggmp21/signing/struct.Presignature.html#method.set_derivation_path), which is malleable to attack that reduces target security level. To mitigate, this method has been removed from API.
* Presignatures + "raw signing" (when signer signs a hash without knowing an original message): results into signature forgery attack \
  Previously, users were able to configure [`Presignature::issue_partial_signature`](https://docs.rs/cggmp21/0.6.3/cggmp21/signing/struct.Presignature.html#method.issue_partial_signature) with hashed message without ever providing original mesage. In new API, this method only accepts digests for which original message has been observed.

### Patches
`cggmp24 v0.7.0-alpha.2` release contains API changes that make it impossible to use presignatures in contexts in which it reduces security. Follow [migration guidelines](https://github.com/LFDT-Lockness/cggmp21/blob/v0.7.0-alpha.2/CGGMP21_MIGRATION.md) to upgrade.

### Workarounds
Users can continue using un-patched versions of library as long as they don't use presignatures in said scenarios where it weakens system security. To be sure, migrate to patched version that excludes presignatures from being used in such scenarios.

### References
Read this [blog post](https://www.dfns.co/article/cggmp21-vulnerabilities-patched-and-explained) to learn more.

## References
- https://github.com/LFDT-Lockness/cggmp21/security/advisories/GHSA-8frv-q972-9rq5
- https://nvd.nist.gov/vuln/detail/CVE-2025-66017
- https://github.com/LFDT-Lockness/cggmp21/commit/9d98157e151596573cb071da59d27a4e0ac9b8dc
- https://github.com/LFDT-Lockness/cggmp21
- https://rustsec.org/advisories/RUSTSEC-2025-0127.html
- https://rustsec.org/advisories/RUSTSEC-2025-0128.html
- https://www.dfns.co/article/cggmp21-vulnerabilities-patched-and-explained
