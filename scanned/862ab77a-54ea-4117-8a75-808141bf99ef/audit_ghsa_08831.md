# [M] russh server userauth state is not reset when authentication principal changes

## Summary
Severity: Medium
Advisory: GHSA-hpv4-5h6f-wqr3
CVE: CVE-2026-46705
CWE: CWE-287
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-hpv4-5h6f-wqr3
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0.34.0-beta.1 <0.61.0

## Details
### Summary
The `russh` server authentication path keeps internal userauth state across `SSH_MSG_USERAUTH_REQUEST` messages without separating that state when the request principal changes.

RFC 4252 allows the `user name` and `service name` fields to change between authentication requests. The issue is not that such changes are invalid. The issue is that russh-owned authentication state, such as remaining methods, partial-success state, and in-progress method state, can remain associated with the connection and then influence a later request for a different `(user, service)`.

This is an internal library state mismatch. Applications are responsible for any authentication state they keep in their own handlers, but russh must reset or separate state that russh itself owns.

### Details
The relevant server-side auth logic is in:

- `russh/src/server/encrypted.rs`
- `russh/src/auth.rs`

RFC 4252 section 5 says the `user name` and `service name` fields are repeated in every `SSH_MSG_USERAUTH_REQUEST` and may change. It also says the server implementation must check those fields in every message and flush accumulated authentication state if they change; if it cannot flush that state, it must disconnect.

In vulnerable `russh` code, the username and service are decoded from each `SSH_MSG_USERAUTH_REQUEST`, while the `AuthRequest` state remains connection-scoped. That state includes:

- `methods`, which is later encoded as the `SSH_MSG_USERAUTH_FAILURE` remaining-methods list.
- `partial_success`, which is later encoded in `SSH_MSG_USERAUTH_FAILURE`.
- `current`, which tracks in-progress method state such as public-key offer or keyboard-interactive challenge state.
- `rejection_count`.

If one request narrows russh's internal `methods` set, a later request for a different user can observe that narrowed set unless the internal state is reset at the principal boundary.

### PoC
The PoC demonstrates only russh-owned state. The handler does not store any cross-request state. Alice's request narrows russh's remaining methods to `password`; Bob's later plain reject should not reuse that internal state.

```rust
struct RemainingMethodsUserSwitchServer;

impl server::Handler for RemainingMethodsUserSwitchServer {
    type Error = russh::Error;

    async fn auth_none(&mut self, user: &str) -> Result<server::Auth, Self::Error> {
        if user == "alice" {
            Ok(server::Auth::Reject {
                proceed_with_methods: Some(MethodSet::from(&[MethodKind::Password][..])),
                partial_success: true,
            })
        } else {
            Ok(server::Auth::reject())
        }
    }
}

#[tokio::test]
async fn auth_does_not_carry_remaining_methods_across_username_change() {
    let alice = session.authenticate_none("alice").await.unwrap();

    assert!(matches!(
        alice,
        client::AuthResult::Failure {
            ref remaining_methods,
            ..
        } if *remaining_methods == MethodSet::from(&[MethodKind::Password][..])
    ));

    let bob = session.authenticate_none("bob").await.unwrap();

    if let client::AuthResult::Failure {
        remaining_methods, ..
    } = bob {
        assert!(
            remaining_methods.contains(&MethodKind::PublicKey),
            "server reused Alice's narrowed remaining methods for Bob: {remaining_methods:?}"
        );
    }
}
```

On `upstream/main`, this fails with:

```text
server reused Alice's narrowed remaining methods for Bob: MethodSet([Password])
```

That failure is produced by russh's retained `AuthRequest.methods`; it does not depend on handler-owned MFA/session state.

### Impact
Suggested provisional CVSS v3.1:

- `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`
- Score: `5.3`

Reasoning:

- `AV:N`: reachable by a remote SSH client during authentication.
- `AC:L`: the attack is a normal sequence of SSH user-auth packets.
- `PR:N`: the attacker does not need an already-authenticated SSH session.
- `UI:N`: no user interaction is required on the server side.
- `S:U`: the impact is within the vulnerable SSH server implementation.
- `C:N`: the narrow PoC does not disclose confidential data.
- `I:L`: russh-owned authentication state for one principal can affect the authentication flow for a different principal.
- `A:N`: the narrow PoC does not demonstrate an availability impact.

This report does not claim that username changes are inherently invalid, nor does it rely on application-owned authentication state being mishandled by the embedding server.

### Fix / Patch Direction
The fix should update russh's internal userauth state handling so that accumulated russh-owned state is flushed or separated when `(user, service)` changes between `SSH_MSG_USERAUTH_REQUEST` messages.

The fix stores the last seen `(user, service)` on `AuthRequest`. When a new auth request arrives for a different principal, russh resets its internal auth state before dispatching the new request. This keeps username changes protocol-valid while preventing prior russh-owned auth state from carrying into the new principal.

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-hpv4-5h6f-wqr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46705
- https://github.com/Eugeny/russh
