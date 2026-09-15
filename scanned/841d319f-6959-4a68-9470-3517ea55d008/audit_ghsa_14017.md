# [M] malformed proposed intoto entries can cause a panic

## Summary
Severity: Medium
Advisory: GHSA-frqx-jfcm-6jjr
CVE: CVE-2023-33199
CWE: CWE-617
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-frqx-jfcm-6jjr
Type: github-advisory

## Affected
- Go: `github.com/sigstore/rekor` — affected >=0 <1.2.0

## Details
### Impact
A malformed proposed entry of the `intoto/v0.0.2` type can cause a panic on a thread within the Rekor process. The thread is recovered so the client receives a 500 error message and service still continues, so the availability impact of this is minimal.

### Patches
This is fixed in v1.2.0 of Rekor.

### Workarounds
No

### References
Discovered by OSS-Fuzz

## References
- https://github.com/sigstore/rekor/security/advisories/GHSA-frqx-jfcm-6jjr
- https://nvd.nist.gov/vuln/detail/CVE-2023-33199
- https://github.com/sigstore/rekor/commit/140c5add105179e5ffd9e3e114fd1b6b93aebbd4
- https://github.com/sigstore/rekor
