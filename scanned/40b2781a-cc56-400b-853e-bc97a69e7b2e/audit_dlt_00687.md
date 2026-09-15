# [?] Fix race condition in `Postman` causing flaky `OfferPayment` tests (#3270)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2026-03-19
Source: https://github.com/ACINQ/eclair/commit/8c5f39f434bf6de32227d7ac92918ec7dd979608
Type: security-commit

## Details
Fix race condition in `Postman` causing flaky `OfferPayment` tests (#3270)

The integration test "send blinded multi-part payment a->b->c (single
channel a->b)" in `OfferPaymentSpec` fails intermittently. The root
cause is a race condition in `Postman` where the subscription for an
onion message reply is registered after the message is sent, allowing
the reply to arrive and be silently dropped before the subscription
exists.

In integration tests where all 3 nodes run on the same JVM, the onion
message round-trip (Alice -> Bob -> Carol -> creates invoice -> Carol
-> Bob -> Alice) can complete in just a few milliseconds - fast enough
to beat the `Subscribe` message to the `Postman`'s mailbox.

This explains why the test is flaky: it usually works (round-trip slower
than subscribe), but occasionally fails (round-trip faster than
subscribe, reply dropped).

We simply move the subscription registration to *before* the message is
sent to the network.
