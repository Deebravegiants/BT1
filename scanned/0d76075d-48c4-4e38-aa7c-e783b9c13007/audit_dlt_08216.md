# [?] Explorer: Fix crash on failed anchor account parsing (#29760)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-01-18
Source: https://github.com/solana-labs/solana/commit/df92d8ff3d5b21594f61687840b89823b302dd8f
Type: security-commit

## Details
Explorer: Fix crash on failed anchor account parsing (#29760)

Fix crash on failed anchor account parsing

## Patch
### explorer/src/components/account/AnchorAccountCard.tsx
```diff
@@ -27,7 +27,11 @@ export function AnchorAccountCard({ account }: { account: Account }) {
       );
       if (accountDefTmp) {
         accountDef = accountDefTmp;
-        decodedAccountData = coder.decode(accountDef.name, rawData);
+        try {
+          decodedAccountData = coder.decode(accountDef.name, rawData);
+        } catch (err) {
+          console.log(err);
+        }
       }
     }
 
```
