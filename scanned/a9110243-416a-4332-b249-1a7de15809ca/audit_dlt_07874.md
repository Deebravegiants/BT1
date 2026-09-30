# [?] fix crash when calling MEV rpc with MEV disabled (#4389)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-12-05
Source: https://github.com/status-im/nimbus-eth2/commit/996a0bdcdc76cb6aa7f9ab38d4e633f321dde823
Type: security-commit

## Details
fix crash when calling MEV rpc with MEV disabled (#4389)

Avoid `/eth/v1/beacon/blinded_blocks` crash without `--payload-builder`.

## Patch
### beacon_chain/validators/message_router_mev.nim
```diff
@@ -48,6 +48,9 @@ proc unblindAndRouteBlockMEV*(
     Future[Result[Opt[BlockRef], string]] {.async.} =
   # By time submitBlindedBlock is called, must already have done slashing
   # protection check
+  if node.payloadBuilderRestClient.isNil:
+    return err "unblindAndRouteBlockMEV: nil REST client"
+
   let unblindedPayload =
     try:
       awaitWithTimeout(
```
