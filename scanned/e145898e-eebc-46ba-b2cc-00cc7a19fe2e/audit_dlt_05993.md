# [?] llmq: harden DKG message-intake against unauthenticated retention and crashes

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-06-30
Source: https://github.com/dashpay/dash/commit/31142da98c8147b0d092d9fa0eff29def5a13b10
Type: security-commit

## Details
llmq: harden DKG message-intake against unauthenticated retention and crashes

Harden the pushed DKG message path (QCONTRIB/QCOMPLAINT/QJUSTIFICATION/QPCOMMITMENT):

- Require the sending peer to be MNAuth-verified (qwatch is unauthenticated and does not bypass this).

- Reject oversized DKG payloads (per-type MaxDKGMessageSize) before deserialization/retention.

- Structurally pre-validate (param-only checks, on a copy) before retention.

- Never feed an invalid BLS signature to CBLSSignature::AggregateInsecure(): the batch verifier skips invalid sigs and per-type PreVerifyMessage rejects them.
