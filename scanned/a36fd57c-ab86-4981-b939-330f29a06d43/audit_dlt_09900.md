# [?] fix: deleting account from remote node during rescan caused crash. Error was that in memory store still contained account for a moment while the head 

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2024-04-03
Source: https://github.com/iron-fish/ironfish/commit/a34552caf7e1ff83a09db364d6ecc19fdf94e287
Type: security-commit

## Details
fix: deleting account from remote node during rescan caused crash. Error was that in memory store still contained account for a moment while the head was deleted. (#4867)

## Patch
### ironfish/src/wallet/wallet.ts
```diff
@@ -1620,6 +1620,7 @@ export class Wallet {
     })
 
     this.accounts.set(account.id, account)
+    this.logger.debug(`Account ${account.id} imported successfully`)
     this.onAccountImported.emit(account)
 
     return account
@@ -1646,6 +1647,7 @@ export class Wallet {
       id: uuid(),
       walletDb: this.walletDb,
     })
+    this.logger.debug(`Resetting account name: ${account.name}, id: ${account.id}`)
 
     await this.walletDb.db.withTransaction(options?.tx, async (tx) => {
       await this.walletDb.setAccount(newAccount, tx)
@@ -1672,6 +1674,7 @@ export class Wallet {
   }
 
   async removeAccount(account: Account, tx?: IDatabaseTransaction): Promise<void> {
+    this.accounts.delete(account.id)
     await this.walletDb.db.withTransaction(tx, async (tx) => {
       if (account.id === this.defaultAccount) {
         await this.walletDb.setDefaultAccount(null, tx)
@@ -1682,7 +1685,7 @@ export class Wallet {
       await this.walletDb.removeHead(account, tx)
     })
 
-    this.accounts.delete(account.id)
+    this.logger.debug(`Removed account name: ${account.name}, id: ${account.id}`)
     this.onAccountRemoved.emit(account)
   }
 
```
