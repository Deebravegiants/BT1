# [?] fix(txpool): race condition in NonceManager.TxWithNonceReceived (#9861)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-12-02
Source: https://github.com/NethermindEth/nethermind/commit/15e3f0d3c06d0b9fcaf2906af955307851943b33
Type: security-commit

## Details
fix(txpool): race condition in NonceManager.TxWithNonceReceived (#9861)

## Patch
### src/Nethermind/Nethermind.TxPool/NonceManager.cs
```diff
@@ -63,8 +63,9 @@ private void TxAccepted()
 
         public NonceLocker TxWithNonceReceived(UInt256 nonce)
         {
+            NonceLocker locker = new(_accountLock, TxAccepted);
             _reservedNonce = nonce;
-            return new(_accountLock, TxAccepted);
+            return locker;
         }
 
         private void ReleaseNonces(UInt256 accountNonce)
```
