# [M] vodozemac's usage of non-constant time base64 decoder could lead to leakage of secret key material

## Summary
Severity: Medium
Advisory: GHSA-j8cm-g7r6-hfpq
CVE: CVE-2024-40640
CWE: CWE-208
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-j8cm-g7r6-hfpq
Type: github-advisory

## Affected
- crates.io: `vodozemac` — affected >=0 <0.7.0

## Details
Versions before 0.7.0 of vodozemac use a non-constant time base64 implementation for importing key material for Megolm group sessions and `PkDecryption` Ed25519 secret keys. This flaw might allow an attacker to infer some information about the secret key material through a side-channel attack.

### Impact

The use of a non-constant time base64 implementation might allow an attacker to observe timing variations in the encoding and decoding operations of the secret key material. This could potentially provide insights into the underlying secret key material.

The impact of this vulnerability is considered low because exploiting the attacker is required to have access to high precision timing measurements, as well as repeated access to the base64 encoding or decoding processes.  Additionally, the estimated leakage amount is bounded and low according to the referenced paper.

### Patches

The patch is in commit 734b6c6948d4b2bdee3dd8b4efa591d93a61d272.

### Workarounds
None.

### References
A detailed description of the precise attack can be found at https://arxiv.org/abs/2108.04600. We kindly thank Soatok for pointing out this research to us.

### For more information
If you have any questions or comments about this advisory please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/vodozemac/security/advisories/GHSA-j8cm-g7r6-hfpq
- https://nvd.nist.gov/vuln/detail/CVE-2024-40640
- https://github.com/matrix-org/vodozemac/commit/734b6c6948d4b2bdee3dd8b4efa591d93a61d272
- https://github.com/matrix-org/vodozemac/commit/77765dace11266ef9523301624a01265c6e0f790
- https://arxiv.org/abs/2108.04600
- https://github.com/matrix-org/vodozemac
- https://rustsec.org/advisories/RUSTSEC-2024-0354.html
