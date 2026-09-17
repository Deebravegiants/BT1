# [H] phonenumber panics on parsing crafted RFC3966 inputs

## Summary
Severity: High
Advisory: GHSA-whhr-7f2w-qqj2
CVE: CVE-2023-42444
CWE: CWE-1284, CWE-248, CWE-392
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-whhr-7f2w-qqj2
Type: github-advisory

## Affected
- crates.io: `phonenumber` — affected >=0 <0.2.5
- crates.io: `phonenumber` — affected >=0.3.0 <0.3.3

## Details
### Impact
The phonenumber parsing code may panic due to a panic-guarded out-of-bounds access on the phonenumber string.

In a typical deployment of `rust-phonenumber`, this may get triggered by feeding a maliciously crafted phonenumber over the network, specifically the string `.;phone-context=`.

### Patches
Patches will be published as version `0.3.3+8.13.9` and backported as `0.2.5+8.11.3`.

### Workarounds
n.a.

### References
n.a.

## References
- https://github.com/whisperfish/rust-phonenumber/security/advisories/GHSA-whhr-7f2w-qqj2
- https://nvd.nist.gov/vuln/detail/CVE-2023-42444
- https://github.com/whisperfish/rust-phonenumber/commit/2dd44be94539c051b4dee55d1d9d349bd7bedde6
- https://github.com/whisperfish/rust-phonenumber/commit/bea8e732b9cada617ede5cf51663dba183747f71
- https://github.com/whisperfish/rust-phonenumber
- https://rustsec.org/advisories/RUSTSEC-2023-0082.html
