# [C] cggmp21 has a missing check in the ZK proof used in CGGMP21

## Summary
Severity: Critical
Advisory: GHSA-m95p-425x-x889
CVE: CVE-2025-66016
CWE: CWE-345, CWE-347
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-m95p-425x-x889
Type: github-advisory

## Affected
- crates.io: `cggmp21` — affected >=0 <0.6.3
- crates.io: `cggmp24` — affected >=0 <0.7.0-alpha.2

## Details
### Impact
cggmp21  concerns a missing check in the ZK proof that enables an attack in which a single malicious signer can reconstruct full private key.

### Patches
* `cggmp21 v0.6.3` is a patch release that contains a fix that introduces this specific missing check
* However, cggmp21 recommends upgrading to `cggmp24 v0.7.0-alpha.2` which contains many other security checks as a precaution. Follow [migration guideline](https://github.com/LFDT-Lockness/cggmp21/blob/v0.7.0-alpha.2/CGGMP21_MIGRATION.md) to upgrade.

### Workarounds
Update to `cggmp21 v0.6.3`, a minor release that contains a minimal security patch.

However, for full mitigation, users will need to upgrade to `cggmp24 v0.7.0-alpha.2` as it contains many more security check implementations.

### Resources
Read this [blog post](https://www.dfns.co/article/cggmp21-vulnerabilities-patched-and-explained) to learn more.

## References
- https://github.com/LFDT-Lockness/cggmp21/security/advisories/GHSA-m95p-425x-x889
- https://nvd.nist.gov/vuln/detail/CVE-2025-66016
- https://github.com/LFDT-Lockness/cggmp21/commit/60e0ada5291e771d5649793329d99edd32285e72
- https://github.com/LFDT-Lockness/cggmp21
- https://rustsec.org/advisories/RUSTSEC-2025-0129.html
- https://rustsec.org/advisories/RUSTSEC-2025-0130.html
- https://www.dfns.co/article/cggmp21-vulnerabilities-patched-and-explained
