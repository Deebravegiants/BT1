# [M] Timing Attack Vulnerability in SCRAM Authentication

## Summary
Severity: Medium
Advisory: GHSA-3wfh-36rx-9537
CVE: CVE-2025-59432
CWE: CWE-208, CWE-385
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-3wfh-36rx-9537
Type: github-advisory

## Affected
- Maven: `com.ongres.scram:scram-common` — affected >=0 <3.2

## Details
### Impact

A timing attack vulnerability exists in the SCRAM Java implementation. The issue arises because `Arrays.equals` was used to compare secret values such as client proofs and server signatures. Since `Arrays.equals` performs a short-circuit comparison, the execution time varies depending on how many leading bytes match. This behavior could allow an attacker to perform a timing side-channel attack and potentially infer sensitive authentication material. All users relying on SCRAM authentication are impacted.

### Patches

This vulnerability has been patched by replacing `Arrays.equals` with `MessageDigest.isEqual`, which ensures constant-time comparison.

Users should upgrade to version **3.2** or later to mitigate this issue.

### Workarounds

Because the attack requires high precision and repeated attempts, the risk is limited, but the only reliable mitigation is to upgrade to a patched release (version 3.2 or later).

### References

- [Java `MessageDigest.isEqual` Documentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/security/MessageDigest.html#isEqual(byte[],byte[]))

## References
- https://github.com/ongres/scram/security/advisories/GHSA-3wfh-36rx-9537
- https://nvd.nist.gov/vuln/detail/CVE-2025-59432
- https://github.com/ongres/scram/commit/e0b0cf99f05406a0d26682c72fcb5728e95124b3
- https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/security/MessageDigest.html#isEqual(byte%5B%5D,byte%5B%5D)
- https://github.com/ongres/scram
