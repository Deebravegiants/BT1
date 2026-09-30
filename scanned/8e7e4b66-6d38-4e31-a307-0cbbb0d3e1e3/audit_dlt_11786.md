# [?] Add paragraph about DoS prevention measures for p2p bids (#4831)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/consensus-specs
Published: 2026-01-13
Source: https://github.com/ethereum/consensus-specs/commit/9bc57220b02795fd2ee132d228829509cbc2ab6d
Type: security-commit

## Details
Add paragraph about DoS prevention measures for p2p bids (#4831)

This PR is an alternative to:

* https://github.com/ethereum/consensus-specs/pull/4792

Rather than define exactly what clients should do, leave it up to them.

## Patch
### specs/gloas/p2p-interface.md
```diff
@@ -321,6 +321,12 @@ The following validations MUST pass before forwarding the
 - _[REJECT]_ `signed_execution_payload_bid.signature` is valid with respect to
   the `bid.builder_index`.
 
+*Note*: Implementations SHOULD include DoS prevention measures to mitigate spam
+from malicious builders submitting numerous bids with minimal value increments.
+Possible strategies include: (1) only forwarding bids that exceed the current
+highest bid by a minimum threshold, or (2) forwarding only the highest observed
+bid at regular time intervals.
+
 ###### `proposer_preferences`
 
 *[New in Gloas:EIP7732]*
```
