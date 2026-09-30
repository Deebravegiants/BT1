# [?] Fix create account / scan race condition (#2079)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-08-22
Source: https://github.com/iron-fish/ironfish/commit/589df44e1cb0901952a7252fb1f29818e43e1087
Type: security-commit

## Details
Fix create account / scan race condition (#2079)

There is a bug where we don't wait for the create account transaction to
complete before we insert the account into the in memory cache, exposing
it to other code to access. This leads to situations where an account
is available to things like rescan, but haven't been added to the
database yet which we require. This leads to crashes where you can load
an account but it'll crash when the headHashes table for that account is
empty.

We need to wait for the TX to commit, before we expose it to in memory,
or set it as the default.

## Patch
### ironfish/src/wallet/wallet.ts
```diff
@@ -925,16 +925,16 @@ export class Accounts {
     })
 
     await this.db.database.transaction(async (tx) => {
-      this.accounts.set(account.id, account)
       await this.db.setAccount(account, tx)
-
       await this.updateHeadHash(account, this.chainProcessor.hash, tx)
-
-      if (setDefault) {
-        await this.setDefaultAccount(account.name, tx)
-      }
     })
 
+    this.accounts.set(account.id, account)
+
+    if (setDefault) {
+      await this.setDefaultAccount(account.name)
+    }
+
     return account
   }
 
```
