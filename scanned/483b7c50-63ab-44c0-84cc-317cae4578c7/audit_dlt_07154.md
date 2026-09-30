# [?] Merge bitcoin/bitcoin#32930: Resolve guix non-determinism with emplace_back instead of push_back

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-07-11
Source: https://github.com/bitcoin/bitcoin/commit/3c1418666bfac88072e0b0c9ce7d156526caf606
Type: security-commit

## Details
Merge bitcoin/bitcoin#32930: Resolve guix non-determinism with emplace_back instead of push_back

f43571010e3853e83a21aa4774b1c8da47b5d961 Resolve guix non-determinism with emplace_back instead of push_back (Ava Chow)

Pull request description:

  For some reason, building x86_64-w64-mingw32 on x86_64 and aarch64 results in a single instruction difference which can be traced down to prevector.h:174. The ultimate caller of this is the copy constructor for a prevector that ends up being called by std::vector::push_back in walletmodel.cpp:183. By replacing the push_back with an emplace_back, somehow this non-determinism goes away.

  Closes #32923

ACKs for top commit:
  l0rinc:
    code review ACK f43571010e3853e83a21aa4774b1c8da47b5d961
  Sjors:
    utACK f43571010e3853e83a21aa4774b1c8da47b5d961
  maflcko:
    lgtm ACK f43571010e3853e83a21aa4774b1c8da47b5d961

Tree-SHA512: 5bf0571f32cb72efc0c533e16d2704cfc3a79bcef2943f0892743572808610fb00ca8ab41223897536f8e5090bf4030735be910942de8116652d02bc3f231e2e

## Patch
### src/qt/walletmodel.cpp
```diff
@@ -179,8 +179,7 @@ WalletModel::SendCoinsReturn WalletModel::prepareTransaction(WalletModelTransact
             setAddress.insert(rcp.address);
             ++nAddresses;
 
-            CRecipient recipient{DecodeDestination(rcp.address.toStdString()), rcp.amount, rcp.fSubtractFeeFromAmount};
-            vecSend.push_back(recipient);
+            vecSend.emplace_back(CRecipient{DecodeDestination(rcp.address.toStdString()), rcp.amount, rcp.fSubtractFeeFromAmount});
 
             total += rcp.amount;
         }
```
