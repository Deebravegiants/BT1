# [?] Fixing crash with subtract fee from amount

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2022-03-07
Source: https://github.com/litecoin-project/litecoin/commit/f23835345412a0f384583774efe27f2f2f06aebd
Type: security-commit

## Details
Fixing crash with subtract fee from amount

## Patch
### src/qt/walletmodel.cpp
```diff
@@ -223,7 +223,7 @@ WalletModel::SendCoinsReturn WalletModel::prepareTransaction(WalletModelTransact
         newTx = m_wallet->createTransaction(vecSend, coin_control_copy, !wallet().privateKeysDisabled() /* sign */, nChangePosRet, nFeeRequired, error);
         transaction.setTransactionFee(nFeeRequired);
         if (fSubtractFeeFromAmount && newTx)
-            transaction.reassignAmounts(nChangePosRet);
+            transaction.reassignAmounts(*m_wallet, nChangePosRet);
 
         if(!newTx)
         {
```

### src/qt/walletmodeltransaction.cpp
```diff
@@ -41,17 +41,18 @@ void WalletModelTransaction::setTransactionFee(const CAmount& newFee)
     fee = newFee;
 }
 
-void WalletModelTransaction::reassignAmounts(int nChangePosRet)
+void WalletModelTransaction::reassignAmounts(interfaces::Wallet& wallet, int nChangePosRet)
 {
-    const CTransaction* walletTransaction = wtx.get();
+    std::vector<CTxOutput> outputs = wtx->GetOutputs();
+
     int i = 0;
     for (QList<SendCoinsRecipient>::iterator it = recipients.begin(); it != recipients.end(); ++it)
     {
         SendCoinsRecipient& rcp = (*it);
         {
             if (i == nChangePosRet)
                 i++;
-            rcp.amount = walletTransaction->vout[i].nValue;
+            rcp.amount = wallet.getValue(outputs[i]);
             i++;
         }
     }
```

### src/qt/walletmodeltransaction.h
```diff
@@ -7,6 +7,7 @@
 
 #include <primitives/transaction.h>
 #include <qt/sendcoinsrecipient.h>
+#include <interfaces/wallet.h>
 
 #include <amount.h>
 
@@ -34,7 +35,7 @@ class WalletModelTransaction
 
     CAmount getTotalTransactionAmount() const;
 
-    void reassignAmounts(int nChangePosRet); // needed for the subtract-fee-from-amount feature
+    void reassignAmounts(interfaces::Wallet& wallet, int nChangePosRet); // needed for the subtract-fee-from-amount feature
 
 private:
     QList<SendCoinsRecipient> recipients;
```
