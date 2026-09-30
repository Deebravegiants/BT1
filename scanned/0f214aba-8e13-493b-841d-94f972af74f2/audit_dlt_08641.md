# [?] fix flaky DoS test (#21093)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-07-08
Source: https://github.com/Chia-Network/chia-blockchain/commit/ad54206f00e3e62233f6d007dec782465f55e95f
Type: security-commit

## Details
fix flaky DoS test (#21093)

## Patch
### chia/_tests/core/server/test_dos.py
```diff
@@ -151,8 +151,13 @@ async def test_large_message_disconnect_and_ban(
                 await time_out_assert(10, lambda: self_hostname in server_1.banned_peers)
 
             print(response)
-            assert response.type == WSMsgType.CLOSE
-            assert response.data == WSCloseCode.MESSAGE_TOO_BIG
+            # aiohttp rejects the oversized frame from its header before reading the payload, so the
+            # server tears down the socket while the ~60MB message is still in flight. The resulting
+            # TCP reset can discard the server's close frame, leaving the client with an abrupt CLOSED
+            # instead of a clean CLOSE carrying the MESSAGE_TOO_BIG code.
+            assert response.type in {WSMsgType.CLOSE, WSMsgType.CLOSED}
+            if response.type == WSMsgType.CLOSE:
+                assert response.data == WSCloseCode.MESSAGE_TOO_BIG
 
     @pytest.mark.anyio
     async def test_bad_handshake_and_ban(
```
