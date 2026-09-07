# [M] Lack of Authentication in OnRecvPacket

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-06-allora
Published: 2024-07-19
Source: https://github.com/sherlock-audit/2024-06-allora-judging/issues/2
Type: sherlock-finding

## Details
defsec

Medium

# Lack of Authentication in OnRecvPacket

## Summary

The Axelar sample code acknowledges the importance of authenticating the message based on the channel ID, in addition to verifying the packet sender. However, the Allora chain's implementation does not include any channel ID/sender authentication logic.

## Vulnerability Detail

In the provided code for the Allora chain's IBC middleware (`gmp/middleware.go`), the `OnRecvPacket` function does not perform authentication based on the channel ID when processing incoming packets. This can potentially lead to security vulnerabilities and allow unauthorized or unintended processing of packets.

Comparing it with the Axelar sample code (`gmp_middleware/middleware.go`), there is a commented-out TODO section that mentions the need for channel ID authentication:

```go
// TODO: authenticate the message with channel-id
if data.Sender != AxelarGMPAcc {
    return ack
}
```

## Impact

Without verifying the channel ID, the middleware may process packets from unintended or unauthorized channels. This can result in the execution of malicious or unexpected actions on the receiving chain.

Axelar Sample : https://github.com/axelarnetwork/evm-cosmos-gmp-sample/blob/main/native-integration/sample-middleware/gmp_middleware.go#L114

## Code Snippet

[ibc_middleware.go#L112-L113](https://github.com/sherlock-audit/2024-06-allora/blob/main/allora-chain/x/ibc/gmp/ibc_middleware.go#L112-L113)

```go
// OnRecvPacket implements the IBCMiddleware interface
func (im IBCMiddleware) OnRecvPacket(
	ctx sdk.Context,
	packet channeltypes.Packet,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-06-allora-judging/issues/2_
