# [M] WebAuthn4J Spring Security Improper signature counter value handling

## Summary
Severity: Medium
Advisory: GHSA-v9hx-v6vf-g36j
CVE: CVE-2023-45669
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-v9hx-v6vf-g36j
Type: github-advisory

## Affected
- Maven: `com.webauthn4j:webauthn4j-spring-security-core` — affected >=0 <0.9.1.RELEASE

## Details
Improper signature counter value handling

### Impact

A flaw was found in webauthn4j-spring-security-core. When an authneticator returns an incremented signature counter value during authentication, webauthn4j-spring-security-core does not properly persist the value, which means cloned authenticator detection does not work.
An attacker who cloned valid authenticator in some way can use the cloned authenticator without being detected.

### Patches

Please upgrade to `com.webauthn4j:webauthn4j-spring-security-core:0.9.1.RELEASE`


### References

For more details about WebAuthn signature counters, see [WebAuthn specification 6.1.1. Signature Counter Considerations](https://www.w3.org/TR/2021/REC-webauthn-2-20210408/#sctn-sign-counter).

### Reporter

This issue was discovered by Michael Budnick (@mbudnick)

## References
- https://github.com/webauthn4j/webauthn4j-spring-security/security/advisories/GHSA-v9hx-v6vf-g36j
- https://nvd.nist.gov/vuln/detail/CVE-2023-45669
- https://github.com/webauthn4j/webauthn4j-spring-security/commit/129700d74d83f9b9a82bf88ebc63707e3cb0a725
- https://github.com/webauthn4j/webauthn4j-spring-security
- https://www.w3.org/TR/2021/REC-webauthn-2-20210408/#sctn-sign-counter
