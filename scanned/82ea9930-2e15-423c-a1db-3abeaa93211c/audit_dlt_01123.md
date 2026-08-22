# [H] libp2p: yamux connection DoS via oversized data frame

## Summary
Severity: High
Chain: libp2p
Component: libp2p
CVE: CVE-2026-73568
CWE: Uncontrolled Resource Consumption
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-hmj8-5xmh-5573
Type: github-advisory

## Details
### Summary
The yamux stream multiplexer in py-libp2p does not validate incoming DATA frame lengths against the receive window before reading the frame body. Any peer that completes a standard libp2p handshake can send a single 12-byte frame claiming a 4 GB body, causing the victim's yamux read loop to block indefinitely. This affects the default `new_host()` configuration and requires no special setup on either side.

### Details
In `libp2p/stream_muxer/yamux/yamux.py` (lines 915 to 926), the `handle_incoming()` method dispatches on frame type. When a DATA frame arrives, it reads the body unconditionally:

```python
elif typ == TYPE_DATA:
    try:
        data = (
            await read_exactly(self.secured_conn, length)
            if length > 0
            else b""
        )
```

The `length` field is taken directly from the wire-decoded frame header, a 32-bit unsigned integer with a maximum value of 4,294,967,295. There is no check that `length` fits within the stream's receive window (`DEFAULT_WINDOW_SIZE = 256 * 1024` bytes). The body read also happens before the code checks whether the referenced `stream_id` even exists in `self.streams` (that check is at line 954), so any stream ID triggers the issue.

`handle_incoming()` itself is a single sequential loop with no timeout around the body read. Once `read_exactly` suspends waiting for data that never comes, the loop cannot process any subsequent frames. Every stream on that yamux connection stops working, and no exception is raised.

The same unguarded call appears in the SYN branch at lines 804 to 806, so a crafted SYN frame with a large length field triggers the same stall.

The yamux specification (section 3.3) explicitly requires the receiver to reset the stream if a sender transmits more data than the receive window allows. py-libp2p does not enforce this on the receiver side. All three comparable implementations do: go-yamux tracks `recvWindow` per stream and returns a `SendWindowExceeded` error on violation; rust-yamux validates frame length against the stream credit; js-libp2p yamux checks frame length against `maxMessageSize`.

### PoC
The harness completes a normal noise handshake and yamux negotiation between two local hosts, confirms yamux is healthy with a pre-attack ping, then writes a single malicious frame directly to the attacker's secured connection. After a short pause, it attempts to open a new stream with a 3-second deadline. The stream open never completes.

File: test_poc.py

```python
"""
author: @tahaafarooq
POC: yamux connection DoS via oversized data frame (connection DoS)
"""
import os
import secrets
import gc
import struct
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-hmj8-5xmh-5573_
