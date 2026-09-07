# [M] Missing Cryptographic Step in cassproject

## Summary
Severity: Medium
Advisory: GHSA-7qcx-4p32-qcmx
CVE: CVE-2022-29229
CWE: CWE-325
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-7qcx-4p32-qcmx
Type: github-advisory

## Affected
- npm: `cassproject` — affected >=0 <1.5.8

## Details
### Impact
CaSS Library, (npm:cassproject) has a missing cryptographic step when storing cryptographic keys that can allow a server administrator access to an account’s cryptographic keys. This affects CaSS servers using standalone username/password authentication, which uses a method that expects e2e cryptographic security of authorization credentials.

### Patches
The issue has been patched in 1.5.8, however, the vulnerable accounts are only resecured when the user next logs in using standalone authentication, as the data required to resecure the account is not available to the server.

### Workarounds
The issue may be mitigated by using SSO or client side certificates to log in. Please note that SSO and client side certificate authentication does not have this expectation of no-knowledge credential access, and cryptographic keys are available to the server administrator.

### References
There are no references at this time.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the CaSS Project Github](https://github.com/cassproject/CASS/issues)
* Email us at [the CaSS Project](mailto:cass@eduworks.com)

## References
- https://github.com/cassproject/CASS/security/advisories/GHSA-7qcx-4p32-qcmx
- https://nvd.nist.gov/vuln/detail/CVE-2022-29229
- https://github.com/cassproject/CASS
- https://github.com/cassproject/CASS/releases/tag/1.5.8
