# [H] OnGres SCRAM silent channel-binding authentication downgrade via unsupported certificate algorithms

## Summary
Severity: High
Advisory: GHSA-p9jg-fcr6-3mhf
CVE: CVE-2026-53712
CWE: CWE-636, CWE-757
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-p9jg-fcr6-3mhf
Type: github-advisory

## Affected
- Maven: `com.ongres.scram:scram-client` — affected >=0 <3.3
- Maven: `com.ongres.scram:scram-common` — affected >=0 <3.3

## Details
## Summary

A flaw in `com.ongres.scram:scram-client` allows an attacker capable of performing a TLS man-in-the-middle (MITM) attack to silently downgrade a connection from `SCRAM-SHA-256-PLUS` (with channel binding) to standard `SCRAM-SHA-256` (without channel binding), bypassing strict client-side enforcement policies.

## Component Breakdown

This occurs due to a two-part failure in `TlsServerEndpoint` when a server presents an `X.509` certificate using a modern signature algorithm that lacks traditional `WITH` naming structures (such as `Ed25519` or post-quantum algorithms):

1. The internal hash derivation method fails to parse the algorithm name, swallows the resulting `NoSuchAlgorithmException, and silently returns an empty byte array via the deprecated `getChannelBindingData()` API.
2. The client builder mistakenly interprets this empty byte array as an environmental absence of channel binding data rather than a cryptographic failure, falling back to non-channel-bound authentication.

## Impact & Scope

This issue only impacts deployments where the downstream application layer explicitly enforces strict channel binding enforcement (e.g., channelBinding=require in pgJDBC).

Drivers operating under a "prefer" or "allow" policy  (used by default) are structurally insulated from an unhandled exception since a fallback to standard SCRAM is within their expected configuration.

## Remediation

Update your project configuration to pull in version 3.3 or later of the SCRAM library, which introduces strict exception propagation and explicit policy controls.

If you are interacting with the `ScramClient` builder API directly (e.g., writing a custom driver or database extension):

- Migrate Deprecated APIs: Stop using `TlsServerEndpoint.getChannelBindingData()`. Transition immediately to `TlsServerEndpoint.getChannelBindingHash()`, which correctly propagates `NoSuchAlgorithmException` up the stack.
- Adopt Explicit Policies: Leverage the newly introduced `ChannelBindingPolicy` API during client construction. Do not rely on implicit parameter presence to dictate your security boundaries.

```java
ScramClient client = ScramClient.builder()
    .advertisedMechanisms(serverMechanisms)
    .username(user)
    .password(pass)
    // Explicitly enforce strict boundaries if needed.
    .channelBindingPolicy(ChannelBindingPolicy.REQUIRE) 
    .channelBinding(TlsServerEndpoint.TLS_SERVER_END_POINT, certHash)
    .build();
```

## References
- https://github.com/ongres/scram/security/advisories/GHSA-p9jg-fcr6-3mhf
- https://github.com/ongres/scram
