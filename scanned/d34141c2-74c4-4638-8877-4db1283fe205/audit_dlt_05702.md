# [?] witnessbeacon: avoid interceptor deadlock

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-06-22
Source: https://github.com/lightningnetwork/lnd/commit/98da7b4a56a75ba2dbf47391d43229fd9696e98a
Type: security-commit

## Details
witnessbeacon: avoid interceptor deadlock

Release the preimage beacon lock before invoking the on-chain
interceptor. The interceptor path can block on the htlcswitch event
loop, while resolution of another held on-chain HTLC can call back
into the beacon to add a preimage.

If interceptor delivery fails after the subscriber was registered,
cancel the subscription before returning the error.

On-chain held entries are replay handles for the interceptor while
contractcourt waits for a preimage or on-chain expiry. Once the resolver
tears down, keeping the handle until the refund timeout can replay a stale
HTLC to a reconnecting interceptor.

Thread a dedicated cleanup signal from the witness subscription cancel path
back through the interceptable switch event loop. The held set only removes
on-chain entries for that signal, leaving off-chain entries under the link
flow lifecycle.
