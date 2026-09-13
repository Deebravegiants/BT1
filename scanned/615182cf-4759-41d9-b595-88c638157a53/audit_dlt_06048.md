# [?] Fixes #1017 — unbounded Stratum input buffer allowing remote memory exhaustion (#1023)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2026-05-29
Source: https://github.com/kaspanet/rusty-kaspa/commit/3cef6adaf2c79cfa34704070a49fe10d712b5729
Type: security-commit

## Details
Fixes #1017 — unbounded Stratum input buffer allowing remote memory exhaustion (#1023)

In spawn_client_listener, each TCP connection accumulated incoming bytes in line_buffer until a \n was received. The buffer had no size limit. A client could send data continuously without a newline (staying within the 5-second per-read timeout) and grow line_buffer without bound for as long as the connection stayed open.

This occurred before JSON-RPC parsing and before miner authorization, so any client reaching the Stratum port (default :5555 / 0.0.0.0:5555) could trigger it.

Fix
Introduced MAX_STRATUM_LINE_BYTES (64 KiB) as the maximum size for an incomplete Stratum line awaiting \n.
Added append_line_data() to check the limit before appending; on rejection the buffer is left unchanged.
In the read loop, if a chunk would exceed the cap, the connection is logged and closed immediately.
Exported both symbols from the crate for testability.
64 KiB is well above legitimate Stratum JSON-RPC messages (typically under 1 KiB) while bounding memory per connection.

Tests
Added five unit tests in bridge/src/tests.rs:

Accepts normal messages under the limit
Accepts incremental chunks up to the limit
Rejects append when the buffer is already at capacity
Rejects a single chunk larger than the limit
Accepts data exactly at the limit, then rejects one byte more
