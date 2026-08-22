# [M] JSON-RPC DoS through Websockets

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-18
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/566
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L50


# Vulnerability details

## Impact

The Websocket service accepts messages for 32MB size.

*File: [repos\node\rpc\websockets.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L50C1-L50C1)*

```go
const (
	messageSizeLimit = 32 * 1024 * 1024 // 32MB

)
(...)
conn.SetReadLimit(messageSizeLimit)
```

This size is 3 times bigger than what Golang accepts by default (10MB) on the HTTP service, while there is no reason that websocket payloads are bigger than HTTP payloads. In addition, there is no rate limiting within the code for the websockets.

As a consequence, an external attacker can **take down** the JSON RPC server by :

- Opening a websocket RPC Connection to Zetachain through Websockets.
- Sending in loop, with parallel workers, malicious Websockets messages (with an unknown method) and a total message size of 32MB.

### Details

When the WebSocket server runs, it listens to the messages with `readLoop()` (L211).

When a message is received, the message body is put in `mb` variable. (L222)

This content will then be used to instance a **msg** variable.

*File: [repos\node\rpc\websockets.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L222)*

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/566_
