# [?] fix(gateway): return errors instead of panicking on unauthenticated lnv2 routes

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/804fc070b8556381f3b5caaa8eab34c2d7f7e857
Type: security-commit

## Details
fix(gateway): return errors instead of panicking on unauthenticated lnv2 routes

`routing_info`, `send_payment` and `create_bolt11_invoice` are registered
with `is_authenticated = false`, and iroh dispatch consults only that
flag, so anyone who can reach the gateway can call them for any
federation it serves. All three resolved the LNv2 client module with
`expect("Must have client module")`.

A federation only has to offer one of the two lightning modules --
`check_federation_network` rejects a federation only when both are
absent -- so an LNv1-only federation is a normal configuration for which
that `expect` always fires. Over iroh a panicking handler exits the
gateway process, and deployments restart it, so this is a boot loop
rather than a single crash.

`public_key_v2` now reports a missing LNv2 module as `None`, which its
two callers already handle, and `send_payment_v2` maps it to an outgoing
payment error. `create_bolt11_invoice_v2` needs no separate change: it
reaches the module only through `routing_info_v2`.

`gateway_pay_bolt11_invoice` had the same shape on the LNv1 side:
`expect("LNv1 invoices should have an amount")` while building the
`OutgoingPaymentStarted` log entry. `validate_outgoing_account` already
reports an amountless invoice as `InvoiceMissingAmount`, but only once
the state machine is under way, which is strictly after the log entry.
Do the check up front and return that same error.

`send_payment_v2` becomes `pub` so the regression test can reach it, next
to the already-public `routing_info_v2`. Both are public API surface in
every sense that matters -- they are served unauthenticated.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9
