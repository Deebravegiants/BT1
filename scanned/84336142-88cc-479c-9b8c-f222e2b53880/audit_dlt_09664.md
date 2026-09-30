# [?] fix: filepath in err string when using Wrapf causes non-determinism (#2040)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2025-10-05
Source: https://github.com/dymensionxyz/dymension/commit/faf6c0b68ffd06c6d72ade2a717d5063c6c9d122
Type: security-commit

## Details
fix: filepath in err string when using Wrapf causes non-determinism (#2040)

fix: filepath in err string when using Wrapf

## Patch
### app/upgrades/v5/types/dymns/params.go
```diff
@@ -204,13 +204,13 @@ func NewParams(
 // Validate checks that the parameters have valid values.
 func (m *Params) Validate() error {
 	if err := m.Price.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "price params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "price params: %v", err.Error())
 	}
 	if err := m.Chains.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "chains params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "chains params: %v", err.Error())
 	}
 	if err := m.Misc.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "misc params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "misc params: %v", err.Error())
 	}
 	return nil
 }
@@ -441,7 +441,7 @@ func validateMiscParams(i interface{}) error {
 	}
 
 	if err := validateEpochIdentifier(m.EndEpochHookIdentifier); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "end epoch hook identifier: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "end epoch hook identifier: %v", err.Error())
 	}
 
 	const minGracePeriodDuration = 30 * // number of days
```

### x/delayedack/ibc_middleware.go
```diff
@@ -133,7 +133,7 @@ func (w IBCMiddleware) OnAcknowledgementPacket(
 	var ack channeltypes.Acknowledgement
 	if err := w.Keeper.Cdc().UnmarshalJSON(acknowledgement, &ack); err != nil {
 		l.Error("Unmarshal acknowledgement.", "err", err)
-		return errorsmod.Wrapf(types.ErrUnknownRequest, "unmarshal ICS-20 transfer packet acknowledgement: %v", err)
+		return errorsmod.Wrapf(types.ErrUnknownRequest, "unmarshal ICS-20 transfer packet acknowledgement: %v", err.Error())
 	}
 
 	transfer, err := w.GetValidTransferWithFinalizationInfo(ctx, packet, commontypes.RollappPacket_ON_ACK)
```

### x/denommetadata/ibc_middleware.go
```diff
@@ -111,7 +111,7 @@ func (im IBCModule) OnAcknowledgementPacket(
 ) error {
 	var ack channeltypes.Acknowledgement
 	if err := transfertypes.ModuleCdc.UnmarshalJSON(acknowledgement, &ack); err != nil {
-		return errorsmod.Wrapf(errortypes.ErrJSONUnmarshal, "unmarshal ICS-20 transfer packet acknowledgement: %v", err)
+		return errorsmod.Wrapf(errortypes.ErrJSONUnmarshal, "unmarshal ICS-20 transfer packet acknowledgement: %v", err.Error())
 	}
 
 	if !ack.Success() {
```

### x/dymns/types/buy_offer.go
```diff
@@ -80,14 +80,14 @@ func (m *BuyOrder) Validate() error {
 	} else if m.OfferPrice.IsNegative() {
 		return errorsmod.Wrap(gerrc.ErrInvalidArgument, "offer price is negative")
 	} else if err := m.OfferPrice.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "offer price is invalid: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "offer price is invalid: %v", err.Error())
 	}
 
 	if m.HasCounterpartyOfferPrice() {
 		if m.CounterpartyOfferPrice.IsNegative() {
 			return errorsmod.Wrap(gerrc.ErrInvalidArgument, "counterparty offer price is negative")
 		} else if err := m.CounterpartyOfferPrice.Validate(); err != nil {
-			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "counterparty offer price is invalid: %v", err)
+			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "counterparty offer price is invalid: %v", err.Error())
 		}
 
 		if m.CounterpartyOfferPrice.Denom != m.OfferPrice.Denom {
```

### x/dymns/types/genesis.go
```diff
@@ -18,13 +18,13 @@ func DefaultGenesis() *GenesisState {
 // Validate checks if the GenesisState is valid.
 func (m GenesisState) Validate() error {
 	if err := (&m.Params).Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "params: %v", err.Error())
 	}
 
 	uniqueNames := make(map[string]struct{})
 	for _, dymName := range m.DymNames {
 		if err := dymName.Validate(); err != nil {
-			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Dym-Name '%s': %v", dymName.Name, err)
+			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Dym-Name '%s': %v", dymName.Name, err.Error())
 		}
 		if _, duplicated := uniqueNames[dymName.Name]; duplicated {
 			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Dym-Name '%s': duplicate name", dymName.Name)
@@ -35,13 +35,13 @@ func (m GenesisState) Validate() error {
 	for _, soBid := range m.SellOrderBids {
 		soBid.Params = nil // treat it as refund name orders
 		if err := soBid.Validate(TypeName); err != nil {
-			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Sell-Order-Bid by '%s': %v", soBid.Bidder, err)
+			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Sell-Order-Bid by '%s': %v", soBid.Bidder, err.Error())
 		}
 	}
 
 	for _, bo := range m.BuyOrders {
 		if err := bo.Validate(); err != nil {
-			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Buy-Order by '%s': %v", bo.Buyer, err)
+			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "Buy-Order by '%s': %v", bo.Buyer, err.Error())
 		}
 	}
 
```

### x/dymns/types/msg_place_sell_order.go
```diff
@@ -32,7 +32,7 @@ func (m *MsgPlaceSellOrder) ValidateBasic() error {
 	so.ExpireAt = 1
 
 	if err := so.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid order: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid order: %v", err.Error())
 	}
 
 	if _, err := sdk.AccAddressFromBech32(m.Owner); err != nil {
```

### x/dymns/types/msg_register_alias.go
```diff
@@ -34,7 +34,7 @@ func (m *MsgRegisterAlias) ValidateBasic() error {
 	if m.ConfirmPayment.IsNil() || m.ConfirmPayment.IsZero() {
 		return errorsmod.Wrap(gerrc.ErrInvalidArgument, "confirm payment is not set")
 	} else if err := m.ConfirmPayment.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid confirm payment: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid confirm payment: %v", err.Error())
 	}
 
 	return nil
```

### x/dymns/types/msg_register_name.go
```diff
@@ -34,7 +34,7 @@ func (m *MsgRegisterName) ValidateBasic() error {
 	if m.ConfirmPayment.IsNil() || m.ConfirmPayment.IsZero() {
 		return errorsmod.Wrap(gerrc.ErrInvalidArgument, "confirm payment is not set")
 	} else if err := m.ConfirmPayment.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid confirm payment: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid confirm payment: %v", err.Error())
 	}
 
 	if len(m.Contact) > MaxDymNameContactLength {
```

### x/dymns/types/msg_update_resolve_address.go
```diff
@@ -22,7 +22,7 @@ func (m *MsgUpdateResolveAddress) ValidateBasic() error {
 
 	_, config := m.GetDymNameConfig()
 	if err := config.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "config is invalid: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "config is invalid: %v", err.Error())
 	}
 
 	if m.ChainId == "" {
```

### x/dymns/types/params.go
```diff
@@ -154,13 +154,13 @@ func NewParams(
 // Validate checks that the parameters have valid values.
 func (m *Params) Validate() error {
 	if err := m.Price.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "price params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "price params: %v", err.Error())
 	}
 	if err := m.Chains.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "chains params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "chains params: %v", err.Error())
 	}
 	if err := m.Misc.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "misc params: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "misc params: %v", err.Error())
 	}
 	return nil
 }
@@ -391,7 +391,7 @@ func validateMiscParams(i interface{}) error {
 	}
 
 	if err := validateEpochIdentifier(m.EndEpochHookIdentifier); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "end epoch hook identifier: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "end epoch hook identifier: %v", err.Error())
 	}
 
 	const minGracePeriodDuration = 30 * // number of days
```

### x/dymns/types/sell_order.go
```diff
@@ -88,14 +88,14 @@ func (m *SellOrder) Validate() error {
 	} else if m.MinPrice.IsNegative() {
 		return errorsmod.Wrap(gerrc.ErrInvalidArgument, "SO min price is negative")
 	} else if err := m.MinPrice.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO min price is invalid: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO min price is invalid: %v", err.Error())
 	}
 
 	if m.HasSetSellPrice() {
 		if m.SellPrice.IsNegative() {
 			return errorsmod.Wrap(gerrc.ErrInvalidArgument, "SO sell price is negative")
 		} else if err := m.SellPrice.Validate(); err != nil {
-			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO sell price is invalid: %v", err)
+			return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO sell price is invalid: %v", err.Error())
 		}
 
 		if m.SellPrice.Denom != m.MinPrice.Denom {
@@ -110,7 +110,7 @@ func (m *SellOrder) Validate() error {
 	if m.HighestBid == nil {
 		// valid, means no bid yet
 	} else if err := m.HighestBid.Validate(m.AssetType); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO highest bid is invalid: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO highest bid is invalid: %v", err.Error())
 	} else if m.HighestBid.Price.IsLT(m.MinPrice) {
 		return errorsmod.Wrap(gerrc.ErrInvalidArgument, "SO highest bid price is less than min price")
 	} else if m.HasSetSellPrice() && m.SellPrice.IsLT(m.HighestBid.Price) {
@@ -139,7 +139,7 @@ func (m *SellOrderBid) Validate(assetType AssetType) error {
 	} else if m.Price.IsNegative() {
 		return errorsmod.Wrap(gerrc.ErrInvalidArgument, "SO bid price is negative")
 	} else if err := m.Price.Validate(); err != nil {
-		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO bid price is invalid: %v", err)
+		return errorsmod.Wrapf(gerrc.ErrInvalidArgument, "SO bid price is invalid: %v", err.Error())
 	}
 
 	if err := ValidateOrderParams(m.Params, assetType); err != nil {
```

### x/iro/keeper/create_plan.go
```diff
@@ -193,7 +193,7 @@ func (m msgServer) CreateStandardLaunchPlan(goCtx context.Context, req *types.Ms
 	// This is needed because params.StandardLaunch.TargetRaise might be in a different denom
 	convertedTargetRaise, err := m.convertTargetRaiseToLiquidityDenom(ctx, params.StandardLaunch.TargetRaise, req.LiquidityDenom)
 	if err != nil {
-		return nil, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "failed to convert target raise to liquidity denom: %v", err)
+		return nil, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "failed to convert target raise to liquidity denom: %v", err.Error())
 	}
 
 	// Calculate M parameter for the bonding curve
@@ -218,7 +218,7 @@ func (m msgServer) CreateStandardLaunchPlan(goCtx context.Context, req *types.Ms
 
 	// Validate the bonding curve
 	if err := bondingCurve.ValidateBasic(); err != nil {
-		return nil, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid bonding curve: %v", err)
+		return nil, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "invalid bonding curve: %v", err.Error())
 	}
 
 	// Create plan using global StandardLaunch parameters
@@ -337,13 +337,13 @@ func (m msgServer) convertTargetRaiseToLiquidityDenom(ctx sdk.Context, targetRai
 	// convert the target raise to the base denom (just in case it's not set in base denom)
 	baseTargetRaise, err := m.tk.CalcCoinInBaseDenom(ctx, targetRaise)
 	if err != nil {
-		return sdk.Coin{}, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "failed to convert target raise to base denom: %v", err)
+		return sdk.Coin{}, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "failed to convert target raise to base denom: %v", err.Error())
 	}
 
 	// now get the target raise in the required liquidity denom
 	liquidityTargetRaise, err := m.tk.CalcBaseInCoin(ctx, baseTargetRaise, liquidityDenom)
 	if err != nil {
-		return sdk.Coin{}, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "failed to convert target raise to liquidity denom: %v", err)
+		return sdk.Coin{}, errorsmod.Wrapf(gerrc.ErrInvalidArgument, "failed to convert target raise to liquidity denom: %v", err.Error())
 	}
 	return liquidityTargetRaise, nil
 }
```
