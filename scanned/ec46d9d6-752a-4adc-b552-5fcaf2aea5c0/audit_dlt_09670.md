# [?] fix: denommetadata ibc middleware panic on non-rollapp transfer  (#383)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2023-11-06
Source: https://github.com/dymensionxyz/dymension/commit/0e7af573a4daf9dba8000248fc7486ac2b42cdb0
Type: security-commit

## Details
fix: denommetadata ibc middleware panic on non-rollapp transfer  (#383)

## Patch
### app/app.go
```diff
@@ -585,7 +585,6 @@ func New(
 		keys[rollappmoduletypes.StoreKey],
 		keys[rollappmoduletypes.MemStoreKey],
 		app.GetSubspace(rollappmoduletypes.ModuleName),
-		app.IBCKeeper.ChannelKeeper,
 	)
 
 	app.SequencerKeeper = *sequencermodulekeeper.NewKeeper(
```

### testutil/keeper/delayedack.go
```diff
@@ -14,8 +14,10 @@ import (
 	connectiontypes "github.com/cosmos/ibc-go/v6/modules/core/03-connection/types"
 	channeltypes "github.com/cosmos/ibc-go/v6/modules/core/04-channel/types"
 	"github.com/cosmos/ibc-go/v6/modules/core/exported"
+	ibctypes "github.com/cosmos/ibc-go/v6/modules/light-clients/07-tendermint/types"
 	"github.com/dymensionxyz/dymension/x/delayedack/keeper"
 	"github.com/dymensionxyz/dymension/x/delayedack/types"
+	rollapptypes "github.com/dymensionxyz/dymension/x/rollapp/types"
 	"github.com/stretchr/testify/require"
 	"github.com/tendermint/tendermint/libs/log"
 	tmproto "github.com/tendermint/tendermint/proto/tendermint/types"
@@ -32,6 +34,10 @@ func (ChannelKeeperStub) GetChannel(ctx sdk.Context, portID, channelID string) (
 	return channeltypes.Channel{}, false
 }
 
+func (ChannelKeeperStub) GetChannelClientState(ctx sdk.Context, portID, channelID string) (string, exported.ClientState, error) {
+	return "", &ibctypes.ClientState{}, nil
+}
+
 type ICS4WrapperStub struct{}
 
 func (ICS4WrapperStub) SendPacket(ctx sdk.Context, chanCap *capabilitytypes.Capability, sourcePort string, sourceChannel string, timeoutHeight clienttypes.Height, timeoutTimestamp uint64, data []byte) (sequence uint64, err error) {
@@ -68,8 +74,8 @@ func (ConnectionKeeperStub) GetConnection(ctx sdk.Context, connectionID string)
 
 type RollappKeeperStub struct{}
 
-func (RollappKeeperStub) ExtractRollappIDFromChannel(ctx sdk.Context, destinationPort string, destinationChannel string) (string, error) {
-	return "", nil
+func (RollappKeeperStub) GetRollapp(ctx sdk.Context, chainID string) (rollapptypes.Rollapp, bool) {
+	return rollapptypes.Rollapp{}, false
 }
 
 func DelayedackKeeper(t testing.TB) (*keeper.Keeper, sdk.Context) {
@@ -96,6 +102,7 @@ func DelayedackKeeper(t testing.TB) (*keeper.Keeper, sdk.Context) {
 		storeKey,
 		memStoreKey,
 		paramsSubspace,
+
 		RollappKeeperStub{},
 		ICS4WrapperStub{},
 		ChannelKeeperStub{},
```

### testutil/keeper/rollapp.go
```diff
@@ -8,49 +8,17 @@ import (
 	"github.com/cosmos/cosmos-sdk/store"
 	storetypes "github.com/cosmos/cosmos-sdk/store/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
-	clienttypes "github.com/cosmos/ibc-go/v6/modules/core/02-client/types"
-	channeltypes "github.com/cosmos/ibc-go/v6/modules/core/04-channel/types"
-	"github.com/cosmos/ibc-go/v6/modules/core/exported"
 
-	capabilitytypes "github.com/cosmos/cosmos-sdk/x/capability/types"
 	typesparams "github.com/cosmos/cosmos-sdk/x/params/types"
 	"github.com/dymensionxyz/dymension/x/rollapp/keeper"
 	"github.com/dymensionxyz/dymension/x/rollapp/types"
 
-	ibctypes "github.com/cosmos/ibc-go/v6/modules/light-clients/07-tendermint/types"
 	"github.com/stretchr/testify/require"
 	"github.com/tendermint/tendermint/libs/log"
 	tmproto "github.com/tendermint/tendermint/proto/tendermint/types"
 	tmdb "github.com/tendermint/tm-db"
 )
 
-// rollappChannelKeeper is a stub of cosmosibckeeper.ChannelKeeper.
-type rollappChannelKeeper struct{}
-
-func (rollappChannelKeeper) GetChannel(ctx sdk.Context, portID, channelID string) (channeltypes.Channel, bool) {
-	return channeltypes.Channel{}, false
-}
-
-func (rollappChannelKeeper) GetNextSequenceSend(ctx sdk.Context, portID, channelID string) (uint64, bool) {
-	return 0, false
-}
-
-func (rollappChannelKeeper) SendPacket(
-	ctx sdk.Context,
-	channelCap *capabilitytypes.Capability,
-	sourcePort string,
-	sourceChannel string,
-	timeoutHeight clienttypes.Height,
-	timeoutTimestamp uint64,
-	data []byte,
-) (uint64, error) {
-	return 0, nil
-}
-
-func (rollappChannelKeeper) GetChannelClientState(ctx sdk.Context, portID, channelID string) (string, exported.ClientState, error) {
-	return "", &ibctypes.ClientState{}, nil
-}
-
 func RollappKeeper(t testing.TB) (*keeper.Keeper, sdk.Context) {
 	storeKey := sdk.NewKVStoreKey(types.StoreKey)
 	memStoreKey := storetypes.NewMemoryStoreKey(types.MemStoreKey)
@@ -75,7 +43,6 @@ func RollappKeeper(t testing.TB) (*keeper.Keeper, sdk.Context) {
 		storeKey,
 		memStoreKey,
 		paramsSubspace,
-		rollappChannelKeeper{},
 	)
 
 	ctx := sdk.NewContext(stateStore, tmproto.Header{}, false, log.NewNopLogger())
```

### x/delayedack/ibc_middleware.go
```diff
@@ -117,13 +117,15 @@ func (im IBCMiddleware) OnRecvPacket(
 	}
 
 	// Check if the packet is destined for a rollapp
-	rollappID, err := im.keeper.GetRollappIDFromPacket(ctx, packet)
+	chainID, err := im.keeper.ExtractChainIDFromChannel(ctx, packet.DestinationPort, packet.DestinationChannel)
 	if err != nil {
-		logger.Error("failed to extract rollappID from channel", "err", err)
-		return im.app.OnRecvPacket(ctx, packet, relayer)
+		logger.Error("Failed to extract chain id from channel", "err", err)
+		return channeltypes.NewErrorAcknowledgement(err)
 	}
-	if rollappID == "" {
-		logger.Debug("skipping IBC transfer OnRecvPacket for non-tendermint chain")
+
+	_, found := im.keeper.GetRollapp(ctx, chainID)
+	if !found {
+		logger.Debug("Skipping IBC transfer OnRecvPacket for non-rollapp chain")
 		return im.app.OnRecvPacket(ctx, packet, relayer)
 	}
 
@@ -144,7 +146,7 @@ func (im IBCMiddleware) OnRecvPacket(
 		Relayer:     relayer,
 		ProofHeight: ibcClientLatestHeight.GetRevisionHeight(),
 	}
-	im.keeper.SetRollappPacket(ctx, rollappID, rollappPacket)
+	im.keeper.SetRollappPacket(ctx, chainID, rollappPacket)
 
 	return nil
 }
```

### x/delayedack/keeper/keeper.go
```diff
@@ -14,6 +14,7 @@ import (
 	channeltypes "github.com/cosmos/ibc-go/v6/modules/core/04-channel/types"
 	porttypes "github.com/cosmos/ibc-go/v6/modules/core/05-port/types"
 	"github.com/cosmos/ibc-go/v6/modules/core/exported"
+	ibctypes "github.com/cosmos/ibc-go/v6/modules/light-clients/07-tendermint/types"
 	"github.com/dymensionxyz/dymension/x/delayedack/types"
 	rollapptypes "github.com/dymensionxyz/dymension/x/rollapp/types"
 	"github.com/tendermint/tendermint/libs/log"
@@ -26,7 +27,7 @@ type (
 		memKey     storetypes.StoreKey
 		paramstore paramtypes.Subspace
 
-		rollappkeeper    types.RollappKeeper
+		rollappKeeper    types.RollappKeeper
 		ics4Wrapper      porttypes.ICS4Wrapper
 		channelKeeper    types.ChannelKeeper
 		connectionKeeper types.ConnectionKeeper
@@ -40,6 +41,7 @@ func NewKeeper(
 	storeKey,
 	memKey storetypes.StoreKey,
 	ps paramtypes.Subspace,
+
 	rollappKeeper types.RollappKeeper,
 	ics4Wrapper porttypes.ICS4Wrapper,
 	channelKeeper types.ChannelKeeper,
@@ -57,7 +59,7 @@ func NewKeeper(
 		storeKey:         storeKey,
 		memKey:           memKey,
 		paramstore:       ps,
-		rollappkeeper:    rollappKeeper,
+		rollappKeeper:    rollappKeeper,
 		ics4Wrapper:      ics4Wrapper,
 		channelKeeper:    channelKeeper,
 		clientKeeper:     clientKeeper,
@@ -70,13 +72,22 @@ func (k Keeper) Logger(ctx sdk.Context) log.Logger {
 	return ctx.Logger().With("module", fmt.Sprintf("x/%s", types.ModuleName))
 }
 
-// GetRollappIDFromPacket retrieves the Rollapp ID from a given packet.
-func (k Keeper) GetRollappIDFromPacket(ctx sdk.Context, packet channeltypes.Packet) (string, error) {
-	rollappID, err := k.rollappkeeper.ExtractRollappIDFromChannel(ctx, packet.DestinationPort, packet.DestinationChannel)
+func (k Keeper) ExtractChainIDFromChannel(ctx sdk.Context, portID string, channelID string) (string, error) {
+	_, clientState, err := k.channelKeeper.GetChannelClientState(ctx, portID, channelID)
 	if err != nil {
-		return "", err
+		return "", fmt.Errorf("failed to extract clientID from channel: %w", err)
+	}
+
+	tmClientState, ok := clientState.(*ibctypes.ClientState)
+	if !ok {
+		return "", nil
 	}
-	return rollappID, nil
+
+	return tmClientState.ChainId, nil
+}
+
+func (k Keeper) GetRollapp(ctx sdk.Context, chainID string) (rollapptypes.Rollapp, bool) {
+	return k.rollappKeeper.GetRollapp(ctx, chainID)
 }
 
 // GetClientState retrieves the client state for a given packet.
```

### x/delayedack/types/expected_keepers.go
```diff
@@ -6,12 +6,14 @@ import (
 	connectiontypes "github.com/cosmos/ibc-go/v6/modules/core/03-connection/types"
 	channeltypes "github.com/cosmos/ibc-go/v6/modules/core/04-channel/types"
 	"github.com/cosmos/ibc-go/v6/modules/core/exported"
+	rollapptypes "github.com/dymensionxyz/dymension/x/rollapp/types"
 )
 
 // ChannelKeeper defines the expected IBC channel keeper
 type ChannelKeeper interface {
 	LookupModuleByChannel(ctx sdk.Context, portID, channelID string) (string, *capabilitytypes.Capability, error)
 	GetChannel(ctx sdk.Context, portID, channelID string) (channeltypes.Channel, bool)
+	GetChannelClientState(ctx sdk.Context, portID, channelID string) (string, exported.ClientState, error)
 }
 
 type ClientKeeper interface {
@@ -23,5 +25,5 @@ type ConnectionKeeper interface {
 }
 
 type RollappKeeper interface {
-	ExtractRollappIDFromChannel(ctx sdk.Context, destinationPort string, destinationChannel string) (string, error)
+	GetRollapp(ctx sdk.Context, chainID string) (rollapp rollapptypes.Rollapp, found bool)
 }
```

### x/denommetadata/ibc_middleware.go
```diff
@@ -121,25 +121,21 @@ func (im IBCMiddleware) OnRecvPacket(
 		return channeltypes.NewErrorAcknowledgement(err)
 	}
 
-	rollappID, err := im.rollappkeeper.ExtractRollappIDFromChannel(ctx, packet.DestinationPort, packet.DestinationChannel)
-	if err != nil {
-		logger.Error("failed to extract rollappID from channel", "err", err)
+	// no-op if the receiver chain is the source chain
+	if transfertypes.ReceiverChainIsSource(packet.GetSourcePort(), packet.GetSourceChannel(), data.Denom) {
+		logger.Debug("Skipping IBC transfer OnRecvPacket for receiver chain being the source chain")
 		return im.app.OnRecvPacket(ctx, packet, relayer)
 	}
-	// no-op if rollappID is empty (i.e transfer from non-dymint chain)
-	if rollappID == "" {
-		logger.Debug("skipping IBC transfer OnRecvPacket for non-tendermint chain")
+
+	chainID, err := im.keeper.ExtractChainIDFromChannel(ctx, packet.DestinationPort, packet.DestinationChannel)
+	if err != nil {
+		logger.Error("Failed to extract chain id from channel", "err", err)
 		return im.app.OnRecvPacket(ctx, packet, relayer)
 	}
 
-	rollapp, found := im.rollappkeeper.GetRollapp(ctx, rollappID)
+	rollapp, found := im.rollappkeeper.GetRollapp(ctx, chainID)
 	if !found {
-		panic("failed to handle IBC transfer packet for non-registered rollapp")
-	}
-
-	// no-op if the receiver chain is the source chain
-	if transfertypes.ReceiverChainIsSource(packet.GetSourcePort(), packet.GetSourceChannel(), data.Denom) {
-		logger.Debug("skipping IBC transfer OnRecvPacket for receiver chain being the source chain")
+		logger.Debug("Skipping denommetadata middleware. Chain is not a rollapp. ", "chain_id", chainID, "err", err)
 		return im.app.OnRecvPacket(ctx, packet, relayer)
 	}
 
@@ -158,19 +154,19 @@ func (im IBCMiddleware) OnRecvPacket(
 	}
 
 	if len(rollapp.TokenMetadata) == 0 {
-		logger.Info("skipping new IBC token for rollapp with no metadata", "rollappID", rollappID, "denom", voucherDenom)
+		logger.Info("skipping new IBC token for rollapp with no metadata", "rollappID", chainID, "denom", voucherDenom)
 		return im.app.OnRecvPacket(ctx, packet, relayer)
 	}
 
 	if im.bankkeeper.HasDenomMetaData(ctx, voucherDenom) {
-		logger.Info("denom metadata already registered", "rollappID", rollappID, "denom", voucherDenom)
+		logger.Info("denom metadata already registered", "rollappID", chainID, "denom", voucherDenom)
 		return im.app.OnRecvPacket(ctx, packet, relayer)
 	}
 
 	for i := range rollapp.TokenMetadata {
 		if rollapp.TokenMetadata[i].Base == data.Denom {
 			metadata := banktypes.Metadata{
-				Description: "auto-generated metadata for " + voucherDenom + " from rollapp " + rollappID,
+				Description: "auto-generated metadata for " + voucherDenom + " from rollapp " + chainID,
 				Base:        voucherDenom,
 				DenomUnits:  make([]*banktypes.DenomUnit, len(rollapp.TokenMetadata[i].DenomUnits)),
 				Display:     rollapp.TokenMetadata[i].Display,
@@ -196,7 +192,7 @@ func (im IBCMiddleware) OnRecvPacket(
 
 			im.bankkeeper.SetDenomMetaData(ctx, metadata)
 
-			logger.Info("registered denom metadata for IBC token", "rollappID", rollappID, "denom", voucherDenom)
+			logger.Info("registered denom metadata for IBC token", "rollappID", chainID, "denom", voucherDenom)
 		}
 	}
 
```

### x/denommetadata/keeper/keeper.go
```diff
@@ -11,6 +11,7 @@ import (
 	clienttypes "github.com/cosmos/ibc-go/v6/modules/core/02-client/types"
 	porttypes "github.com/cosmos/ibc-go/v6/modules/core/05-port/types"
 	ibcexported "github.com/cosmos/ibc-go/v6/modules/core/exported"
+	ibctypes "github.com/cosmos/ibc-go/v6/modules/light-clients/07-tendermint/types"
 	"github.com/tendermint/tendermint/libs/log"
 
 	"github.com/dymensionxyz/dymension/x/denommetadata/types"
@@ -58,6 +59,20 @@ func (k Keeper) Logger(ctx sdk.Context) log.Logger {
 	return ctx.Logger().With("module", fmt.Sprintf("x/%s", types.ModuleName))
 }
 
+func (k Keeper) ExtractChainIDFromChannel(ctx sdk.Context, portID string, channelID string) (string, error) {
+	_, clientState, err := k.channelKeeper.GetChannelClientState(ctx, portID, channelID)
+	if err != nil {
+		return "", fmt.Errorf("failed to extract clientID from channel: %w", err)
+	}
+
+	tmClientState, ok := clientState.(*ibctypes.ClientState)
+	if !ok {
+		return "", nil
+	}
+
+	return tmClientState.ChainId, nil
+}
+
 // SendPacket wraps IBC ChannelKeeper's SendPacket function
 func (k Keeper) SendPacket(
 	ctx sdk.Context,
```

### x/denommetadata/types/expected_keepers.go
```diff
@@ -7,6 +7,7 @@ import (
 	capabilitytypes "github.com/cosmos/cosmos-sdk/x/capability/types"
 	"github.com/cosmos/ibc-go/v6/modules/apps/transfer/types"
 	channeltypes "github.com/cosmos/ibc-go/v6/modules/core/04-channel/types"
+	"github.com/cosmos/ibc-go/v6/modules/core/exported"
 )
 
 // TransferKeeper defines the expected transfer keeper
@@ -21,4 +22,5 @@ type ChannelKeeper interface {
 	GetPacketCommitment(ctx sdk.Context, portID, channelID string, sequence uint64) []byte
 	GetNextSequenceSend(ctx sdk.Context, portID, channelID string) (uint64, bool)
 	LookupModuleByChannel(ctx sdk.Context, portID, channelID string) (string, *capabilitytypes.Capability, error)
+	GetChannelClientState(ctx sdk.Context, portID, channelID string) (string, exported.ClientState, error)
 }
```

### x/rollapp/keeper/ibc.go
```diff
@@ -1,22 +0,0 @@
-package keeper
-
-import (
-	"fmt"
-
-	sdk "github.com/cosmos/cosmos-sdk/types"
-	ibctypes "github.com/cosmos/ibc-go/v6/modules/light-clients/07-tendermint/types"
-)
-
-func (k Keeper) ExtractRollappIDFromChannel(ctx sdk.Context, portID string, channelID string) (string, error) {
-	_, clientState, err := k.channelKeeper.GetChannelClientState(ctx, portID, channelID)
-	if err != nil {
-		return "", fmt.Errorf("failed to extract clientID from channel: %w", err)
-	}
-
-	tmClientState, ok := clientState.(*ibctypes.ClientState)
-	if !ok {
-		return "", nil
-	}
-
-	return tmClientState.ChainId, nil
-}
```

### x/rollapp/keeper/keeper.go
```diff
@@ -14,12 +14,11 @@ import (
 
 type (
 	Keeper struct {
-		cdc           codec.BinaryCodec
-		storeKey      storetypes.StoreKey
-		memKey        storetypes.StoreKey
-		hooks         types.MultiRollappHooks
-		paramstore    paramtypes.Subspace
-		channelKeeper types.ChannelKeeper
+		cdc        codec.BinaryCodec
+		storeKey   storetypes.StoreKey
+		memKey     storetypes.StoreKey
+		hooks      types.MultiRollappHooks
+		paramstore paramtypes.Subspace
 	}
 )
 
@@ -28,7 +27,6 @@ func NewKeeper(
 	storeKey,
 	memKey storetypes.StoreKey,
 	ps paramtypes.Subspace,
-	channelKeeper types.ChannelKeeper,
 
 ) *Keeper {
 	// set KeyTable if it has not already been set
@@ -38,12 +36,11 @@ func NewKeeper(
 
 	return &Keeper{
 
-		cdc:           cdc,
-		storeKey:      storeKey,
-		memKey:        memKey,
-		paramstore:    ps,
-		hooks:         nil,
-		channelKeeper: channelKeeper,
+		cdc:        cdc,
+		storeKey:   storeKey,
+		memKey:     memKey,
+		paramstore: ps,
+		hooks:      nil,
 	}
 }
 
```

### x/rollapp/types/expected_keepers.go
```diff
@@ -3,7 +3,6 @@ package types
 import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/cosmos/cosmos-sdk/x/auth/types"
-	"github.com/cosmos/ibc-go/v6/modules/core/exported"
 )
 
 // AccountKeeper defines the expected account keeper used for simulations (noalias)
@@ -17,7 +16,3 @@ type BankKeeper interface {
 	SpendableCoins(ctx sdk.Context, addr sdk.AccAddress) sdk.Coins
 	// Methods imported from bank should be defined here
 }
-
-type ChannelKeeper interface {
-	GetChannelClientState(ctx sdk.Context, portID, channelID string) (string, exported.ClientState, error)
-}
```
