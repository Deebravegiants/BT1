# [C] panic on parsing crafted phonenumber inputs

## Summary
Severity: Critical
Advisory: GHSA-mjw4-jj88-v687
CVE: CVE-2024-39697
CWE: CWE-1284, CWE-248, CWE-392
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-09
Source: https://github.com/advisories/GHSA-mjw4-jj88-v687
Type: github-advisory

## Affected
- crates.io: `phonenumber` — affected >=0.3.4 <0.3.6

## Details
### Impact
The phonenumber parsing code may panic due to a reachable `assert!` guard on the phonenumber string.

In a typical deployment of rust-phonenumber, this may get triggered by feeding a maliciously crafted phonenumber, e.g. over the network, specifically strings of the form `+dwPAA;phone-context=AA`, where the "number" part potentially parses as a number larger than 2^56.

Since f69abee1/0.3.4/#52.

0.2.x series is not affected.

### Patches
Upgrade to 0.3.6 or higher.

### Workarounds
n/a

### References
Whereas https://github.com/whisperfish/rust-phonenumber/issues/69 did not provide an example code path, property testing found a few: `+dwPAA;phone-context=AA`.

## References
- https://github.com/whisperfish/rust-phonenumber/security/advisories/GHSA-mjw4-jj88-v687
- https://nvd.nist.gov/vuln/detail/CVE-2024-39697
- https://github.com/whisperfish/rust-phonenumber/issues/69
- https://github.com/whisperfish/rust-phonenumber/pull/52
- https://github.com/whisperfish/rust-phonenumber/commit/b792151b17fc90231c232a23935830c2266f3203
- https://github.com/whisperfish/rust-phonenumber/commit/f69abee1481fac0d6d531407bae90020e39c6407
- https://github.com/whisperfish/rust-phonenumber
- https://rustsec.org/advisories/RUSTSEC-2024-0369.html
