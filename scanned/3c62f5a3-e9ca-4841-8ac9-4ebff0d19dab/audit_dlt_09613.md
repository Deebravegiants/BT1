# [?] fix!: fix non-deterministic upgrade code (#3004) (#3008)

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2024-03-18
Source: https://github.com/cosmos/gaia/commit/7ace7417fd816e6150f569f4ddd1d9911996cf46
Type: security-commit

## Details
fix!: fix non-deterministic upgrade code (#3004) (#3008)

Co-authored-by: MSalopek <matija.salopek994@gmail.com>

## Patch
### app/upgrades/v15/upgrades.go
```diff
@@ -393,9 +393,9 @@ Discrepancy #3:
 // UpgradeEscrowAccounts mints the necessary assets to reach parity between the escrow account
 // and the counterparty total supply, and then, send them from the transfer module to the escrow account.
 func UpgradeEscrowAccounts(ctx sdk.Context, bankKeeper bankkeeper.Keeper, transferKeeper ibctransferkeeper.Keeper) {
-	for addr, assets := range GetEscrowUpdates(ctx) {
-		escrowAddress := sdk.MustAccAddressFromBech32(addr)
-		for _, coin := range assets {
+	for _, update := range GetEscrowUpdates(ctx) {
+		escrowAddress := sdk.MustAccAddressFromBech32(update.Address)
+		for _, coin := range update.Coins {
 			coins := sdk.NewCoins(coin)
 
 			if err := bankKeeper.MintCoins(ctx, ibctransfertypes.ModuleName, coins); err != nil {
@@ -414,21 +414,28 @@ func UpgradeEscrowAccounts(ctx sdk.Context, bankKeeper bankkeeper.Keeper, transf
 	}
 }
 
-func GetEscrowUpdates(ctx sdk.Context) map[string]sdk.Coins {
-	escrowUpdates := map[string]sdk.Coins{
-		// discrepancy #1
-		"cosmos1x54ltnyg88k0ejmk8ytwrhd3ltm84xehrnlslf": {
-			{
+type UpdateCoins struct {
+	Address string
+	Coins   sdk.Coins
+}
+
+func GetEscrowUpdates(ctx sdk.Context) []UpdateCoins {
+	escrowUpdates := []UpdateCoins{
+		{
+			// discrepancy #1
+			Address: "cosmos1x54ltnyg88k0ejmk8ytwrhd3ltm84xehrnlslf",
+			Coins: sdk.Coins{{
 				Denom:  "ibc/4925E6ABA571A44D2BE0286D2D29AF42A294D0FF2BB16490149A1B26EAD33729",
 				Amount: sdk.NewInt(40000000000000000),
-			},
+			}},
 		},
-		// discrepancy #2
-		"cosmos1ju6tlfclulxumtt2kglvnxduj5d93a64r5czge": {
-			{
+		{
+			// discrepancy #2
+			Address: "cosmos1ju6tlfclulxumtt2kglvnxduj5d93a64r5czge",
+			Coins: sdk.Coins{{
 				Denom:  "ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC",
 				Amount: sdk.NewInt(2000),
-			},
+			}},
 		},
 	}
 
@@ -439,12 +446,12 @@ func GetEscrowUpdates(ctx sdk.Context) map[string]sdk.Coins {
 	if amt, ok := sdk.NewIntFromString("4388000000000000000000"); !ok {
 		ctx.Logger().Error("can't upgrade missing amount in escrow account: '4388000000000000000000'")
 	} else {
-		coins := escrowUpdates["cosmos1x54ltnyg88k0ejmk8ytwrhd3ltm84xehrnlslf"]
+		coins := escrowUpdates[0].Coins
 		coins = coins.Add(sdk.NewCoins(sdk.NewCoin(
 			"ibc/F5ED5F3DC6F0EF73FA455337C027FE91ABCB375116BF51A228E44C493E020A09",
 			amt,
 		))...)
-		escrowUpdates["cosmos1x54ltnyg88k0ejmk8ytwrhd3ltm84xehrnlslf"] = coins
+		escrowUpdates[0].Coins = coins
 	}
 
 	return escrowUpdates
```

### app/upgrades/v15/upgrades_test.go
```diff
@@ -294,9 +294,9 @@ func TestUpgradeEscrowAccounts(t *testing.T) {
 	escrowUpdates := v15.GetEscrowUpdates(ctx)
 
 	// check escrow accounts are empty
-	for addr, coins := range escrowUpdates {
-		require.Empty(t, bankKeeper.GetAllBalances(ctx, sdk.MustAccAddressFromBech32(addr)))
-		for _, coin := range coins {
+	for _, update := range escrowUpdates {
+		require.Empty(t, bankKeeper.GetAllBalances(ctx, sdk.MustAccAddressFromBech32(update.Address)))
+		for _, coin := range update.Coins {
 			require.Equal(t, sdk.ZeroInt(), transferKeeper.GetTotalEscrowForDenom(ctx, coin.Denom).Amount)
 		}
 	}
@@ -306,9 +306,9 @@ func TestUpgradeEscrowAccounts(t *testing.T) {
 
 	// check that new assets are minted and transferred to the escrow accounts
 	numUpdate := 0
-	for addr, coins := range escrowUpdates {
-		for _, coin := range coins {
-			require.Equal(t, coin, bankKeeper.GetBalance(ctx, sdk.MustAccAddressFromBech32(addr), coin.Denom))
+	for _, update := range escrowUpdates {
+		for _, coin := range update.Coins {
+			require.Equal(t, coin, bankKeeper.GetBalance(ctx, sdk.MustAccAddressFromBech32(update.Address), coin.Denom))
 			// check that the total escrow amount for the denom is updated
 			require.Equal(t, coin, transferKeeper.GetTotalEscrowForDenom(ctx, coin.Denom))
 			numUpdate++
```
