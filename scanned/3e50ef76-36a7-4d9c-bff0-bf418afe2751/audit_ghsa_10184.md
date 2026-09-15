# [M] Sigstore Timestamp Authority has Improper Certificate Validation in verifier

## Summary
Severity: Medium
Advisory: GHSA-xm5m-wgh2-rrg3
CVE: CVE-2026-39984
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-xm5m-wgh2-rrg3
Type: github-advisory

## Affected
- Go: `github.com/sigstore/timestamp-authority/v2` — affected >=0 <2.0.6

## Details
### Authorization bypass via certificate bag manipulation in sigstore/timestamp-authority verifier

An authorization bypass vulnerability exists in sigstore/timestamp-authority verifier (timestamp-authority/v2/pkg/verification): `VerifyTimestampResponse` function correctly verifies the certificate chain but when the TSA specific constraints are verified in `VerifyLeafCert`, the first non-CA certificate from the PKCS#7 certificate bag is used instead of the leaf certificate from the certificate chain. An attacker can exploit this by prepending a forged certificate to the certificate bag while the message is signed with an authorized key. The library validates the signature using the one certificate but performs authorization checks on the another, allowing an attacker to bypass some authorization controls. 

This vulnerability does **not** apply to timestamp-authority service, only to users of `timestamp-authority/v2/pkg/verification` package.

This vulnerability does **not** apply to sigstore-go even though it is a user of `timestamp-authority/v2/pkg/verification`: Providing `TSACertificate` option to  `VerifyTimestampResponse` fully mitigates the issue.


### Patches

The issue will be fixed in timestamp-authority 2.0.6

### Workarounds

Users of `VerifyTimestampResponse` can use the `TSACertificate` option to specify the exact certificate they expect to be used: this fully mitigates the issue.

### References

This issue was found after reading CVE-2026-33753 / GHSA-3xxc-pwj6-jgrj (originally reported by @Jaynornj and @Pr00fOf3xpl0it)

## References
- https://github.com/sigstore/timestamp-authority/security/advisories/GHSA-xm5m-wgh2-rrg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-39984
- https://github.com/sigstore/timestamp-authority
- https://github.com/sigstore/timestamp-authority/releases/tag/v2.0.6
