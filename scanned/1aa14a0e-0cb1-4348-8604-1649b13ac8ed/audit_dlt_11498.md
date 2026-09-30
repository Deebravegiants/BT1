# [?] Fix the race condition by putting the setters at the end of the function (#1091)

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2023-10-12
Source: https://github.com/pyth-network/pyth-crosschain/commit/b158f28c58a03dbd376efba387a7919b390540f1
Type: security-commit

## Details
Fix the race condition by putting the setters at the end of the function (#1091)

## Patch
### governance/xc_admin/packages/xc_admin_frontend/hooks/useMultisig.ts
```diff
@@ -101,39 +101,31 @@ export const useMultisig = (): MultisigHookData => {
           wallet: new NodeWallet(new Keypair()),
         })
         if (cancelled) return
-        setUpgradeMultisigAccount(
-          await readOnlySquads.getMultisig(UPGRADE_MULTISIG[multisigCluster])
+        const upgradeMultisigAccount = await readOnlySquads.getMultisig(
+          UPGRADE_MULTISIG[multisigCluster]
+        )
+
+        if (cancelled) return
+        const priceFeedMultisigAccount = await readOnlySquads.getMultisig(
+          PRICE_FEED_MULTISIG[multisigCluster]
         )
-        try {
-          if (cancelled) return
-          setPriceFeedMultisigAccount(
-            await readOnlySquads.getMultisig(
-              PRICE_FEED_MULTISIG[multisigCluster]
-            )
-          )
-        } catch (e) {
-          console.error(e)
-          setPriceFeedMultisigAccount(undefined)
-        }
 
         if (cancelled) return
         const upgradeProposals = await getSortedProposals(
           readOnlySquads,
           UPGRADE_MULTISIG[multisigCluster]
         )
+
+        if (cancelled) return
+        const sortedPriceFeedMultisigProposals = await getSortedProposals(
+          readOnlySquads,
+          PRICE_FEED_MULTISIG[multisigCluster]
+        )
+
+        setUpgradeMultisigAccount(upgradeMultisigAccount)
+        setPriceFeedMultisigAccount(priceFeedMultisigAccount)
         setUpgradeMultisigProposals(upgradeProposals)
-        try {
-          if (cancelled) return
-          const sortedPriceFeedMultisigProposals = await getSortedProposals(
-            readOnlySquads,
-            PRICE_FEED_MULTISIG[multisigCluster]
-          )
-          setPriceFeedMultisigProposals(sortedPriceFeedMultisigProposals)
-        } catch (e) {
-          console.error(e)
-          setAllProposalsIxsParsed([])
-          setPriceFeedMultisigProposals([])
-        }
+        setPriceFeedMultisigProposals(sortedPriceFeedMultisigProposals)
 
         setIsLoading(false)
       } catch (e) {
```
