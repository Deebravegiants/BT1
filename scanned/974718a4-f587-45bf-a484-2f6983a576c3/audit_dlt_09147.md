# [?] Fix(core/scripts):  removes panic and adds node public keys to peer (#15950)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-01-16
Source: https://github.com/smartcontractkit/chainlink/commit/f9dd7e13bc952e1f006f7e5c663b0953aa565cce
Type: security-commit

## Details
Fix(core/scripts):  removes panic and adds node public keys to peer (#15950)

* fix(core/scripts): adds encrypted public key to peer

* chore: bumps changeset

## Patch
### .changeset/eight-meals-march.md
```diff
@@ -0,0 +1,7 @@
+---
+"chainlink": patch
+---
+
+Prevents a panic in test helper for confirming transaction
+and adds encrypted public key to a peer before calling addNodes
+on CapabilitiesRegistry
```

### core/scripts/common/helpers.go
```diff
@@ -298,6 +298,11 @@ func TenderlySimLink(simID string) string {
 
 // ConfirmTXMined confirms that the given transaction is mined and prints useful execution information.
 func ConfirmTXMined(context context.Context, client *ethclient.Client, transaction *types.Transaction, chainID int64, txInfo ...string) (receipt *types.Receipt) {
+	if transaction == nil {
+		fmt.Println("No transaction to confirm")
+		return
+	}
+
 	fmt.Println("Executing TX", ExplorerLink(chainID, transaction.Hash()), txInfo)
 	receipt, err := bind.WaitMined(context, client, transaction)
 	PanicErr(err)
```

### core/scripts/keystone/src/88_capabilities_registry_helpers.go
```diff
@@ -554,13 +554,23 @@ func peerToNode(nopID uint32, p peer) (kcr.CapabilitiesRegistryNodeParams, error
 		return kcr.CapabilitiesRegistryNodeParams{}, fmt.Errorf("failed to convert signer: %w", err)
 	}
 
+	epk := strings.TrimPrefix(p.EncryptionPublicKey, "0x")
+	epkB, err := hex.DecodeString(epk)
+	if err != nil {
+		return kcr.CapabilitiesRegistryNodeParams{}, fmt.Errorf("failed to convert encryptionPublicKey: %w", err)
+	}
+
+	var epkb [32]byte
+	copy(epkb[:], epkB)
+
 	var sigb [32]byte
 	copy(sigb[:], signerB)
 
 	return kcr.CapabilitiesRegistryNodeParams{
-		NodeOperatorId: nopID,
-		P2pId:          peerIDB,
-		Signer:         sigb,
+		NodeOperatorId:      nopID,
+		P2pId:               peerIDB,
+		Signer:              sigb,
+		EncryptionPublicKey: epkb,
 	}, nil
 }
 
```
