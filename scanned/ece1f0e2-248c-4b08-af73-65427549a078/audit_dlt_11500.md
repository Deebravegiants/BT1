# [?] Fix race condition once and for all (#847)

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2023-05-27
Source: https://github.com/pyth-network/pyth-crosschain/commit/ce8e064c98c0e1f4ac7cba4ed22741cdca6e95e8
Type: security-commit

## Details
Fix race condition once and for all (#847)

## Patch
### governance/xc_admin/packages/xc_admin_frontend/components/tabs/General.tsx
```diff
@@ -324,18 +324,16 @@ const General = ({ proposerServerUrl }: { proposerServerUrl: string }) => {
           )
 
           // create add publisher instruction if there are any publishers
-          if (newChanges.priceAccounts[0].publishers.length > 0) {
-            newChanges.priceAccounts[0].publishers.forEach(
-              (publisherKey: string) => {
-                pythProgramClient.methods
-                  .addPublisher(new PublicKey(publisherKey))
-                  .accounts({
-                    fundingAccount,
-                    priceAccount: priceAccountKey,
-                  })
-                  .instruction()
-                  .then((instruction) => instructions.push(instruction))
-              }
+
+          for (let publisherKey of newChanges.priceAccounts[0].publishers) {
+            instructions.push(
+              await pythProgramClient.methods
+                .addPublisher(new PublicKey(publisherKey))
+                .accounts({
+                  fundingAccount,
+                  priceAccount: priceAccountKey,
+                })
+                .instruction()
             )
           }
 
@@ -438,28 +436,31 @@ const General = ({ proposerServerUrl }: { proposerServerUrl: string }) => {
           )
 
           // add instructions to remove publishers
-          publisherKeysToRemove.forEach((publisherKey: string) => {
-            pythProgramClient.methods
-              .delPublisher(new PublicKey(publisherKey))
-              .accounts({
-                fundingAccount,
-                priceAccount: new PublicKey(prev.priceAccounts[0].address),
-              })
-              .instruction()
-              .then((instruction) => instructions.push(instruction))
-          })
+
+          for (let publisherKey of publisherKeysToRemove) {
+            instructions.push(
+              await pythProgramClient.methods
+                .delPublisher(new PublicKey(publisherKey))
+                .accounts({
+                  fundingAccount,
+                  priceAccount: new PublicKey(prev.priceAccounts[0].address),
+                })
+                .instruction()
+            )
+          }
 
           // add instructions to add new publishers
-          publisherKeysToAdd.forEach((publisherKey: string) => {
-            pythProgramClient.methods
-              .addPublisher(new PublicKey(publisherKey))
-              .accounts({
-                fundingAccount,
-                priceAccount: new PublicKey(prev.priceAccounts[0].address),
-              })
-              .instruction()
-              .then((instruction) => instructions.push(instruction))
-          })
+          for (let publisherKey of publisherKeysToAdd) {
+            instructions.push(
+              await pythProgramClient.methods
+                .addPublisher(new PublicKey(publisherKey))
+                .accounts({
+                  fundingAccount,
+                  priceAccount: new PublicKey(prev.priceAccounts[0].address),
+                })
+                .instruction()
+            )
+          }
         }
       }
 
```
