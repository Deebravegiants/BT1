# [?] Merge pull request from GHSA-832c-mq9v-367r

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2022-09-20
Source: https://github.com/cosmos/ibc-go/commit/02dc44eb03cec3575f0cb0a4a89c576ceeac034c
Type: security-commit

## Details
Merge pull request from GHSA-832c-mq9v-367r

* fix: use block app hash and tx list to generate interchain account address

Generate interchain account addresses using host connection ID, controller PortID, block app hash, and block data hash
Update tests to handle non-determinstic address creation
Add test case to ensure address generation is block dependent

* fix: return error on existing non-interchainaccounts for generated address

If an account exists and is not an interchain account return an error
Add test cases for existing accounts, both interchain and non interchain account
Refactor account tests to be table tests

* fix: refactor handshake code to account for block dependent address generation

* add more test cases, update error messaging

* self review fix

* increase test readability

* add test cases for controller side channel reopening

* chore: fix godoc

## Patch
### modules/apps/27-interchain-accounts/controller/ibc_middleware_test.go
```diff
@@ -7,7 +7,6 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	capabilitytypes "github.com/cosmos/cosmos-sdk/x/capability/types"
 	"github.com/stretchr/testify/suite"
-	"github.com/tendermint/tendermint/crypto"
 
 	"github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/controller"
 	"github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/controller/types"
@@ -20,12 +19,6 @@ import (
 )
 
 var (
-	// TODO: Cosmos-SDK ADR-28: Update crypto.AddressHash() when sdk uses address.Module()
-	// https://github.com/cosmos/cosmos-sdk/issues/10225
-	//
-	// TestAccAddress defines a reusable bech32 address for testing purposes
-	TestAccAddress = icatypes.GenerateAddress(sdk.AccAddress(crypto.AddressHash([]byte(icatypes.ModuleName))), ibctesting.FirstConnectionID, TestPortID)
-
 	// TestOwnerAddress defines a reusable bech32 address for testing purposes
 	TestOwnerAddress = "cosmos17dtl0mjt3t77kpuhg2edqzjpszulwhgzuj9ljs"
 
@@ -570,7 +563,7 @@ func (suite *InterchainAccountsTestSuite) TestOnRecvPacket() {
 				0,
 			)
 
-			ack := cbs.OnRecvPacket(suite.chainA.GetContext(), packet, TestAccAddress)
+			ack := cbs.OnRecvPacket(suite.chainA.GetContext(), packet, nil)
 			suite.Require().Equal(tc.expPass, ack.Success())
 		})
 	}
```

### modules/apps/27-interchain-accounts/controller/keeper/genesis_test.go
```diff
@@ -4,12 +4,14 @@ import (
 	"github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/controller/keeper"
 	"github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/controller/types"
 	genesistypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/genesis/types"
+	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
 	ibctesting "github.com/cosmos/ibc-go/v5/testing"
 )
 
 func (suite *KeeperTestSuite) TestInitGenesis() {
 	suite.SetupTest()
 
+	interchainAccAddr := icatypes.GenerateAddress(suite.chainB.GetContext(), ibctesting.FirstConnectionID, TestPortID)
 	genesisState := genesistypes.ControllerGenesisState{
 		ActiveChannels: []genesistypes.ActiveChannel{
 			{
@@ -23,7 +25,7 @@ func (suite *KeeperTestSuite) TestInitGenesis() {
 			{
 				ConnectionId:   ibctesting.FirstConnectionID,
 				PortId:         TestPortID,
-				AccountAddress: TestAccAddress.String(),
+				AccountAddress: interchainAccAddr.String(),
 			},
 		},
 		Ports: []string{TestPortID},
@@ -40,7 +42,7 @@ func (suite *KeeperTestSuite) TestInitGenesis() {
 
 	accountAdrr, found := suite.chainA.GetSimApp().ICAControllerKeeper.GetInterchainAccountAddress(suite.chainA.GetContext(), ibctesting.FirstConnectionID, TestPortID)
 	suite.Require().True(found)
-	suite.Require().Equal(TestAccAddress.String(), accountAdrr)
+	suite.Require().Equal(interchainAccAddr.String(), accountAdrr)
 
 	expParams := types.NewParams(false)
 	params := suite.chainA.GetSimApp().ICAControllerKeeper.GetParams(suite.chainA.GetContext())
@@ -56,13 +58,16 @@ func (suite *KeeperTestSuite) TestExportGenesis() {
 	err := SetupICAPath(path, TestOwnerAddress)
 	suite.Require().NoError(err)
 
+	interchainAccAddr, exists := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+	suite.Require().True(exists)
+
 	genesisState := keeper.ExportGenesis(suite.chainA.GetContext(), suite.chainA.GetSimApp().ICAControllerKeeper)
 
 	suite.Require().Equal(path.EndpointA.ChannelID, genesisState.ActiveChannels[0].ChannelId)
 	suite.Require().Equal(path.EndpointA.ChannelConfig.PortID, genesisState.ActiveChannels[0].PortId)
 	suite.Require().True(genesisState.ActiveChannels[0].IsMiddlewareEnabled)
 
-	suite.Require().Equal(TestAccAddress.String(), genesisState.InterchainAccounts[0].AccountAddress)
+	suite.Require().Equal(interchainAccAddr, genesisState.InterchainAccounts[0].AccountAddress)
 	suite.Require().Equal(path.EndpointA.ChannelConfig.PortID, genesisState.InterchainAccounts[0].PortId)
 
 	suite.Require().Equal([]string{TestPortID}, genesisState.GetPorts())
```

### modules/apps/27-interchain-accounts/controller/keeper/grpc_query_test.go
```diff
@@ -4,7 +4,6 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 
 	"github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/controller/types"
-	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
 	ibctesting "github.com/cosmos/ibc-go/v5/testing"
 )
 
@@ -64,10 +63,11 @@ func (suite *KeeperTestSuite) TestQueryInterchainAccount() {
 			res, err := suite.chainA.GetSimApp().ICAControllerKeeper.InterchainAccount(sdk.WrapSDKContext(suite.chainA.GetContext()), req)
 
 			if tc.expPass {
-				expAddress := icatypes.GenerateAddress(suite.chainA.GetSimApp().AccountKeeper.GetModuleAddress(icatypes.ModuleName), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				expAddress, exists := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				suite.Require().True(exists)
 
 				suite.Require().NoError(err)
-				suite.Require().Equal(expAddress.String(), res.Address)
+				suite.Require().Equal(expAddress, res.Address)
 			} else {
 				suite.Require().Error(err)
 			}
```

### modules/apps/27-interchain-accounts/controller/keeper/handshake_test.go
```diff
@@ -24,9 +24,7 @@ func (suite *KeeperTestSuite) TestOnChanOpenInit() {
 	}{
 		{
 			"success",
-			func() {
-				path.EndpointA.SetChannel(*channel)
-			},
+			func() {},
 			true,
 		},
 		{
@@ -54,30 +52,44 @@ func (suite *KeeperTestSuite) TestOnChanOpenInit() {
 			},
 			true,
 		},
+		{
+			"success: channel reopening",
+			func() {
+				err := SetupICAPath(path, TestOwnerAddress)
+				suite.Require().NoError(err)
+
+				err = path.EndpointA.SetChannelClosed()
+				suite.Require().NoError(err)
+
+				err = path.EndpointB.SetChannelClosed()
+				suite.Require().NoError(err)
+
+				path.EndpointA.ChannelID = ""
+				path.EndpointB.ChannelID = ""
+			},
+			true,
+		},
 		{
 			"invalid metadata -  previous metadata is different",
 			func() {
 				// set active channel to closed
 				suite.chainA.GetSimApp().ICAControllerKeeper.SetActiveChannelID(suite.chainA.GetContext(), ibctesting.FirstConnectionID, path.EndpointA.ChannelConfig.PortID, path.EndpointA.ChannelID)
 
+				// attempt to downgrade version by reinitializing channel with version 1, but setting channel to version 2
+				metadata.Version = "ics27-2"
+
+				versionBytes, err := icatypes.ModuleCdc.MarshalJSON(&metadata)
+				suite.Require().NoError(err)
+
 				counterparty := channeltypes.NewCounterparty(path.EndpointB.ChannelConfig.PortID, path.EndpointB.ChannelID)
 				closedChannel := channeltypes.Channel{
 					State:          channeltypes.CLOSED,
 					Ordering:       channeltypes.ORDERED,
 					Counterparty:   counterparty,
 					ConnectionHops: []string{path.EndpointA.ConnectionID},
-					Version:        TestVersion,
+					Version:        string(versionBytes),
 				}
-
 				path.EndpointA.SetChannel(closedChannel)
-
-				// modify metadata
-				metadata.Version = "ics27-2"
-
-				versionBytes, err := icatypes.ModuleCdc.MarshalJSON(&metadata)
-				suite.Require().NoError(err)
-
-				channel.Version = string(versionBytes)
 			},
 			false,
 		},
@@ -384,7 +396,10 @@ func (suite *KeeperTestSuite) TestOnChanOpenAck() {
 			err = path.EndpointB.ChanOpenTry()
 			suite.Require().NoError(err)
 
-			metadata = icatypes.NewMetadata(icatypes.Version, ibctesting.FirstConnectionID, ibctesting.FirstConnectionID, TestAccAddress.String(), icatypes.EncodingProtobuf, icatypes.TxTypeSDKMultiMsg)
+			interchainAccAddr, exists := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+			suite.Require().True(exists)
+
+			metadata = icatypes.NewMetadata(icatypes.Version, ibctesting.FirstConnectionID, ibctesting.FirstConnectionID, interchainAccAddr, icatypes.EncodingProtobuf, icatypes.TxTypeSDKMultiMsg)
 			versionBytes, err := icatypes.ModuleCdc.MarshalJSON(&metadata)
 			suite.Require().NoError(err)
 
```

### modules/apps/27-interchain-accounts/controller/keeper/keeper_test.go
```diff
@@ -3,9 +3,7 @@ package keeper_test
 import (
 	"testing"
 
-	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/stretchr/testify/suite"
-	"github.com/tendermint/tendermint/crypto"
 
 	genesistypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/genesis/types"
 	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
@@ -14,12 +12,6 @@ import (
 )
 
 var (
-	// TODO: Cosmos-SDK ADR-28: Update crypto.AddressHash() when sdk uses address.Module()
-	// https://github.com/cosmos/cosmos-sdk/issues/10225
-	//
-	// TestAccAddress defines a reusable bech32 address for testing purposes
-	TestAccAddress = icatypes.GenerateAddress(sdk.AccAddress(crypto.AddressHash([]byte(icatypes.ModuleName))), ibctesting.FirstConnectionID, TestPortID)
-
 	// TestOwnerAddress defines a reusable bech32 address for testing purposes
 	TestOwnerAddress = "cosmos17dtl0mjt3t77kpuhg2edqzjpszulwhgzuj9ljs"
 
@@ -153,11 +145,10 @@ func (suite *KeeperTestSuite) TestGetInterchainAccountAddress() {
 	suite.Require().NoError(err)
 
 	counterpartyPortID := path.EndpointA.ChannelConfig.PortID
-	expectedAddr := icatypes.GenerateAddress(suite.chainA.GetSimApp().AccountKeeper.GetModuleAddress(icatypes.ModuleName), ibctesting.FirstConnectionID, counterpartyPortID)
 
 	retrievedAddr, found := suite.chainA.GetSimApp().ICAControllerKeeper.GetInterchainAccountAddress(suite.chainA.GetContext(), ibctesting.FirstConnectionID, counterpartyPortID)
 	suite.Require().True(found)
-	suite.Require().Equal(expectedAddr.String(), retrievedAddr)
+	suite.Require().NotEmpty(retrievedAddr)
 
 	retrievedAddr, found = suite.chainA.GetSimApp().ICAControllerKeeper.GetInterchainAccountAddress(suite.chainA.GetContext(), "invalid conn", "invalid port")
 	suite.Require().False(found)
@@ -214,13 +205,16 @@ func (suite *KeeperTestSuite) TestGetAllInterchainAccounts() {
 	err := SetupICAPath(path, TestOwnerAddress)
 	suite.Require().NoError(err)
 
+	interchainAccAddr, exists := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+	suite.Require().True(exists)
+
 	suite.chainA.GetSimApp().ICAControllerKeeper.SetInterchainAccountAddress(suite.chainA.GetContext(), ibctesting.FirstConnectionID, expectedPortID, expectedAccAddr)
 
 	expectedAccounts := []genesistypes.RegisteredInterchainAccount{
 		{
 			ConnectionId:   ibctesting.FirstConnectionID,
 			PortId:         TestPortID,
-			AccountAddress: TestAccAddress.String(),
+			AccountAddress: interchainAccAddr,
 		},
 		{
 			ConnectionId:   ibctesting.FirstConnectionID,
```

### modules/apps/27-interchain-accounts/controller/keeper/msg_server_test.go
```diff
@@ -124,13 +124,13 @@ func (suite *KeeperTestSuite) TestSubmitTx() {
 		},
 		{
 			"failure - active channel does not exist for port ID", func() {
-				msg.Owner = TestAccAddress.String()
+				msg.Owner = "invalid-owner"
 			},
 			false,
 		},
 		{
 			"failure - controller module does not own capability for this channel", func() {
-				msg.Owner = TestAccAddress.String()
+				msg.Owner = "invalid-owner"
 				portID, err := icatypes.NewControllerPortID(msg.Owner)
 				suite.Require().NoError(err)
 
```

### modules/apps/27-interchain-accounts/host/ibc_module_test.go
```diff
@@ -10,7 +10,6 @@ import (
 	capabilitytypes "github.com/cosmos/cosmos-sdk/x/capability/types"
 	"github.com/gogo/protobuf/proto"
 	"github.com/stretchr/testify/suite"
-	"github.com/tendermint/tendermint/crypto"
 
 	"github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/host/types"
 	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
@@ -22,12 +21,6 @@ import (
 )
 
 var (
-	// TODO: Cosmos-SDK ADR-28: Update crypto.AddressHash() when sdk uses address.Module()
-	// https://github.com/cosmos/cosmos-sdk/issues/10225
-	//
-	// TestAccAddress defines a reusable bech32 address for testing purposes
-	TestAccAddress = icatypes.GenerateAddress(sdk.AccAddress(crypto.AddressHash([]byte(icatypes.ModuleName))), ibctesting.FirstConnectionID, TestPortID)
-
 	// TestOwnerAddress defines a reusable bech32 address for testing purposes
 	TestOwnerAddress = "cosmos17dtl0mjt3t77kpuhg2edqzjpszulwhgzuj9ljs"
 
@@ -148,6 +141,17 @@ func (suite *InterchainAccountsTestSuite) TestOnChanOpenTry() {
 		{
 			"success", func() {}, true,
 		},
+		{
+			"account address generation is block dependent", func() {
+				icaHostAccount := icatypes.GenerateAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				err := suite.chainB.GetSimApp().BankKeeper.SendCoins(suite.chainB.GetContext(), suite.chainB.SenderAccount.GetAddress(), icaHostAccount, sdk.Coins{sdk.NewCoin("stake", sdk.NewInt(1))})
+				suite.Require().NoError(err)
+				suite.Require().True(suite.chainB.GetSimApp().AccountKeeper.HasAccount(suite.chainB.GetContext(), icaHostAccount))
+
+				// ensure account registration is simulated in a separate block
+				suite.chainB.NextBlock()
+			}, true,
+		},
 		{
 			"host submodule disabled", func() {
 				suite.chainB.GetSimApp().ICAHostKeeper.SetParams(suite.chainB.GetContext(), types.NewParams(false, []string{}))
@@ -214,6 +218,10 @@ func (suite *InterchainAccountsTestSuite) TestOnChanOpenTry() {
 
 			if tc.expPass {
 				suite.Require().NoError(err)
+
+				addr, exists := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, counterparty.PortId)
+				suite.Require().True(exists)
+				suite.Require().NotNil(addr)
 			} else {
 				suite.Require().Error(err)
 				suite.Require().Equal("", version)
@@ -527,7 +535,7 @@ func (suite *InterchainAccountsTestSuite) TestOnAcknowledgementPacket() {
 				0,
 			)
 
-			err = cbs.OnAcknowledgementPacket(suite.chainB.GetContext(), packet, []byte("ackBytes"), TestAccAddress)
+			err = cbs.OnAcknowledgementPacket(suite.chainB.GetContext(), packet, []byte("ackBytes"), nil)
 
 			if tc.expPass {
 				suite.Require().NoError(err)
@@ -580,7 +588,7 @@ func (suite *InterchainAccountsTestSuite) TestOnTimeoutPacket() {
 				0,
 			)
 
-			err = cbs.OnTimeoutPacket(suite.chainA.GetContext(), packet, TestAccAddress)
+			err = cbs.OnTimeoutPacket(suite.chainA.GetContext(), packet, nil)
 
 			if tc.expPass {
 				suite.Require().NoError(err)
@@ -606,21 +614,28 @@ func (suite *InterchainAccountsTestSuite) fundICAWallet(ctx sdk.Context, portID
 	suite.Require().NoError(err)
 }
 
-// TestControlAccountAfterChannelClose tests that a controller chain can control a registered interchain account after the currently active channel for that interchain account has been closed
-// by opening a new channel on the associated portID
+// TestControlAccountAfterChannelClose tests that a controller chain can control a registered interchain account after the currently active channel for that interchain account has been closed.
+// A new channel will be opened for the controller portID. The interchain account address should remain unchanged.
 func (suite *InterchainAccountsTestSuite) TestControlAccountAfterChannelClose() {
-	// create channel + init interchain account on a particular port
 	path := NewICAPath(suite.chainA, suite.chainB)
 	suite.coordinator.SetupConnections(path)
+
 	err := SetupICAPath(path, TestOwnerAddress)
 	suite.Require().NoError(err)
 
+	// two sends will be performed, one after initial creation of the account and one after channel closure and reopening
+	var (
+		startingBal           = sdk.NewCoins(sdk.NewCoin(sdk.DefaultBondDenom, sdk.NewInt(100000)))
+		tokenAmt              = sdk.NewCoins(sdk.NewCoin(sdk.DefaultBondDenom, sdk.NewInt(5000)))
+		expBalAfterFirstSend  = startingBal.Sub(tokenAmt...)
+		expBalAfterSecondSend = expBalAfterFirstSend.Sub(tokenAmt...)
+	)
+
 	// check that the account is working as expected
-	suite.fundICAWallet(suite.chainB.GetContext(), path.EndpointA.ChannelConfig.PortID, sdk.NewCoins(sdk.NewCoin(sdk.DefaultBondDenom, sdk.NewInt(10000))))
-	interchainAccountAddr, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), ibctesting.FirstConnectionID, path.EndpointA.ChannelConfig.PortID)
+	suite.fundICAWallet(suite.chainB.GetContext(), path.EndpointA.ChannelConfig.PortID, startingBal)
+	interchainAccountAddr, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
 	suite.Require().True(found)
 
-	tokenAmt := sdk.NewCoins(sdk.NewCoin(sdk.DefaultBondDenom, sdk.NewInt(5000)))
 	msg := &banktypes.MsgSend{
 		FromAddress: interchainAccountAddr,
 		ToAddress:   suite.chainB.SenderAccount.GetAddress().String(),
@@ -651,8 +666,7 @@ func (suite *InterchainAccountsTestSuite) TestControlAccountAfterChannelClose()
 	icaAddr, err := sdk.AccAddressFromBech32(interchainAccountAddr)
 	suite.Require().NoError(err)
 
-	hasBalance := suite.chainB.GetSimApp().BankKeeper.HasBalance(suite.chainB.GetContext(), icaAddr, sdk.Coin{Denom: sdk.DefaultBondDenom, Amount: sdk.NewInt(5000)})
-	suite.Require().True(hasBalance)
+	suite.assertBalance(icaAddr, expBalAfterFirstSend)
 
 	// close the channel
 	err = path.EndpointA.SetChannelClosed()
@@ -674,7 +688,12 @@ func (suite *InterchainAccountsTestSuite) TestControlAccountAfterChannelClose()
 	err = path.RelayPacket(packetRelay)
 	suite.Require().NoError(err) // relay committed
 
-	// check that the ica balance is updated
-	hasBalance = suite.chainB.GetSimApp().BankKeeper.HasBalance(suite.chainB.GetContext(), icaAddr, sdk.Coin{Denom: sdk.DefaultBondDenom, Amount: sdk.NewInt(0)})
-	suite.Require().True(hasBalance)
+	suite.assertBalance(icaAddr, expBalAfterSecondSend)
+}
+
+// assertBalance asserts that the provided address has exactly the expected balance.
+// CONTRACT: the expected balance must only contain one coin denom.
+func (suite *InterchainAccountsTestSuite) assertBalance(addr sdk.AccAddress, expBalance sdk.Coins) {
+	balance := suite.chainB.GetSimApp().BankKeeper.GetBalance(suite.chainB.GetContext(), addr, sdk.DefaultBondDenom)
+	suite.Require().Equal(expBalance[0], balance)
 }
```

### modules/apps/27-interchain-accounts/host/keeper/account.go
```diff
@@ -2,17 +2,20 @@ package keeper
 
 import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
+	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
 	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
 
 	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
 )
 
-// RegisterInterchainAccount attempts to create a new account using the provided address and
-// stores it in state keyed by the provided connection and port identifiers
-// If an account for the provided address already exists this function returns early (no-op)
-func (k Keeper) RegisterInterchainAccount(ctx sdk.Context, connectionID, controllerPortID string, accAddress sdk.AccAddress) {
+// createInterchainAccount creates a new interchain account. An address is generated using the host connectionID, the controller portID,
+// and block dependent information. An error is returned if an account already exists for the generated account.
+// An interchain account type is set in the account keeper and the interchain account address mapping is updated.
+func (k Keeper) createInterchainAccount(ctx sdk.Context, connectionID, controllerPortID string) (sdk.AccAddress, error) {
+	accAddress := icatypes.GenerateAddress(ctx, connectionID, controllerPortID)
+
 	if acc := k.accountKeeper.GetAccount(ctx, accAddress); acc != nil {
-		return
+		return nil, sdkerrors.Wrapf(icatypes.ErrAccountAlreadyExist, "existing account for newly generated interchain account address %s", accAddress)
 	}
 
 	interchainAccount := icatypes.NewInterchainAccount(
@@ -24,4 +27,6 @@ func (k Keeper) RegisterInterchainAccount(ctx sdk.Context, connectionID, control
 	k.accountKeeper.SetAccount(ctx, interchainAccount)
 
 	k.SetInterchainAccountAddress(ctx, connectionID, controllerPortID, interchainAccount.Address)
+
+	return accAddress, nil
 }
```

### modules/apps/27-interchain-accounts/host/keeper/account_test.go
```diff
@@ -1,33 +0,0 @@
-package keeper_test
-
-import (
-	sdk "github.com/cosmos/cosmos-sdk/types"
-
-	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
-	ibctesting "github.com/cosmos/ibc-go/v5/testing"
-)
-
-func (suite *KeeperTestSuite) TestRegisterInterchainAccount() {
-	suite.SetupTest()
-
-	path := NewICAPath(suite.chainA, suite.chainB)
-	suite.coordinator.SetupConnections(path)
-
-	// RegisterInterchainAccount
-	err := SetupICAPath(path, TestOwnerAddress)
-	suite.Require().NoError(err)
-
-	portID, err := icatypes.NewControllerPortID(TestOwnerAddress)
-	suite.Require().NoError(err)
-
-	// Get the address of the interchain account stored in state during handshake step
-	storedAddr, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), ibctesting.FirstConnectionID, portID)
-	suite.Require().True(found)
-
-	icaAddr, err := sdk.AccAddressFromBech32(storedAddr)
-	suite.Require().NoError(err)
-
-	// Check if account is created
-	interchainAccount := suite.chainB.GetSimApp().AccountKeeper.GetAccount(suite.chainB.GetContext(), icaAddr)
-	suite.Require().Equal(interchainAccount.GetAddress().String(), storedAddr)
-}
```

### modules/apps/27-interchain-accounts/host/keeper/genesis_test.go
```diff
@@ -11,6 +11,8 @@ import (
 func (suite *KeeperTestSuite) TestInitGenesis() {
 	suite.SetupTest()
 
+	interchainAccAddr := icatypes.GenerateAddress(suite.chainB.GetContext(), ibctesting.FirstConnectionID, TestPortID)
+
 	genesisState := genesistypes.HostGenesisState{
 		ActiveChannels: []genesistypes.ActiveChannel{
 			{
@@ -23,7 +25,7 @@ func (suite *KeeperTestSuite) TestInitGenesis() {
 			{
 				ConnectionId:   ibctesting.FirstConnectionID,
 				PortId:         TestPortID,
-				AccountAddress: TestAccAddress.String(),
+				AccountAddress: interchainAccAddr.String(),
 			},
 		},
 		Port: icatypes.PortID,
@@ -37,7 +39,7 @@ func (suite *KeeperTestSuite) TestInitGenesis() {
 
 	accountAdrr, found := suite.chainA.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainA.GetContext(), ibctesting.FirstConnectionID, TestPortID)
 	suite.Require().True(found)
-	suite.Require().Equal(TestAccAddress.String(), accountAdrr)
+	suite.Require().Equal(interchainAccAddr.String(), accountAdrr)
 
 	expParams := types.NewParams(false, nil)
 	params := suite.chainA.GetSimApp().ICAHostKeeper.GetParams(suite.chainA.GetContext())
@@ -53,12 +55,15 @@ func (suite *KeeperTestSuite) TestExportGenesis() {
 	err := SetupICAPath(path, TestOwnerAddress)
 	suite.Require().NoError(err)
 
+	interchainAccAddr, exists := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+	suite.Require().True(exists)
+
 	genesisState := keeper.ExportGenesis(suite.chainB.GetContext(), suite.chainB.GetSimApp().ICAHostKeeper)
 
 	suite.Require().Equal(path.EndpointB.ChannelID, genesisState.ActiveChannels[0].ChannelId)
 	suite.Require().Equal(path.EndpointA.ChannelConfig.PortID, genesisState.ActiveChannels[0].PortId)
 
-	suite.Require().Equal(TestAccAddress.String(), genesisState.InterchainAccounts[0].AccountAddress)
+	suite.Require().Equal(interchainAccAddr, genesisState.InterchainAccounts[0].AccountAddress)
 	suite.Require().Equal(path.EndpointA.ChannelConfig.PortID, genesisState.InterchainAccounts[0].PortId)
 
 	suite.Require().Equal(icatypes.PortID, genesisState.GetPort())
```

### modules/apps/27-interchain-accounts/host/keeper/handshake.go
```diff
@@ -70,10 +70,25 @@ func (k Keeper) OnChanOpenTry(
 		return "", sdkerrors.Wrapf(err, "failed to claim capability for channel %s on port %s", channelID, portID)
 	}
 
-	accAddress := icatypes.GenerateAddress(k.accountKeeper.GetModuleAddress(icatypes.ModuleName), metadata.HostConnectionId, counterparty.PortId)
+	var (
+		accAddress sdk.AccAddress
+		err        error
+	)
 
-	// Register interchain account if it does not already exist
-	k.RegisterInterchainAccount(ctx, metadata.HostConnectionId, counterparty.PortId, accAddress)
+	interchainAccAddr, found := k.GetInterchainAccountAddress(ctx, metadata.HostConnectionId, counterparty.PortId)
+	if found {
+		// reopening an interchain account
+		accAddress = sdk.MustAccAddressFromBech32(interchainAccAddr)
+		if _, ok := k.accountKeeper.GetAccount(ctx, accAddress).(*icatypes.InterchainAccount); !ok {
+			return "", sdkerrors.Wrapf(icatypes.ErrInvalidAccountReopening, "existing account address %s, does not have interchain account type", accAddress)
+		}
+
+	} else {
+		accAddress, err = k.createInterchainAccount(ctx, metadata.HostConnectionId, counterparty.PortId)
+		if err != nil {
+			return "", err
+		}
+	}
 
 	metadata.Address = accAddress.String()
 	versionBytes, err := icatypes.ModuleCdc.MarshalJSON(&metadata)
```

### modules/apps/27-interchain-accounts/host/keeper/handshake_test.go
```diff
@@ -1,14 +1,43 @@
 package keeper_test
 
 import (
+	sdk "github.com/cosmos/cosmos-sdk/types"
+	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
 	capabilitytypes "github.com/cosmos/cosmos-sdk/x/capability/types"
 
+	hosttypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/host/types"
 	icatypes "github.com/cosmos/ibc-go/v5/modules/apps/27-interchain-accounts/types"
 	channeltypes "github.com/cosmos/ibc-go/v5/modules/core/04-channel/types"
 	host "github.com/cosmos/ibc-go/v5/modules/core/24-host"
 	ibctesting "github.com/cosmos/ibc-go/v5/testing"
 )
 
+// open and close channel is a helper function for TestOnChanOpenTry for reopening accounts
+func (suite *KeeperTestSuite) openAndCloseChannel(path *ibctesting.Path) {
+	err := path.EndpointB.ChanOpenTry()
+	suite.Require().NoError(err)
+
+	err = path.EndpointA.ChanOpenAck()
+	suite.Require().NoError(err)
+
+	err = path.EndpointB.ChanOpenConfirm()
+	suite.Require().NoError(err)
+
+	err = path.EndpointA.SetChannelClosed()
+	suite.Require().NoError(err)
+
+	err = path.EndpointB.SetChannelClosed()
+	suite.Require().NoError(err)
+
+	path.EndpointA.ChannelID = ""
+	err = RegisterInterchainAccount(path.EndpointA, TestOwnerAddress)
+	suite.Require().NoError(err)
+
+	// bump channel sequence as these test mock core IBC behaviour on ChanOpenTry
+	channelSequence := path.EndpointB.Chain.App.GetIBCKeeper().ChannelKeeper.GetNextChannelSequence(path.EndpointB.Chain.GetContext())
+	path.EndpointB.ChannelID = channeltypes.FormatChannelIdentifier(channelSequence)
+}
+
 func (suite *KeeperTestSuite) TestOnChanOpenTry() {
 	var (
 		channel  *channeltypes.Channel
@@ -24,22 +53,89 @@ func (suite *KeeperTestSuite) TestOnChanOpenTry() {
 	}{
 		{
 			"success",
-			func() {
-				path.EndpointB.SetChannel(*channel)
-			},
+			func() {},
 			true,
 		},
 		{
 			"success - reopening closed active channel",
 			func() {
-				// create a new channel and set it in state
-				ch := channeltypes.NewChannel(channeltypes.CLOSED, channeltypes.ORDERED, channeltypes.NewCounterparty(path.EndpointA.ChannelConfig.PortID, path.EndpointA.ChannelID), []string{path.EndpointA.ConnectionID}, TestVersion)
-				suite.chainB.GetSimApp().GetIBCKeeper().ChannelKeeper.SetChannel(suite.chainB.GetContext(), path.EndpointB.ChannelConfig.PortID, path.EndpointB.ChannelID, ch)
+				// create interchain account
+				// undo setup
+				path.EndpointB.ChannelID = ""
+				err := suite.chainB.App.GetScopedIBCKeeper().ReleaseCapability(suite.chainB.GetContext(), chanCap)
+				suite.Require().NoError(err)
 
-				// set the active channelID in state
-				suite.chainB.GetSimApp().ICAHostKeeper.SetActiveChannelID(suite.chainB.GetContext(), ibctesting.FirstConnectionID, path.EndpointA.ChannelConfig.PortID, path.EndpointB.ChannelID)
+				suite.openAndCloseChannel(path)
+			}, true,
+		},
+		{
+			"success - reopening account with new address",
+			func() {
+				// create interchain account
+				// undo setup
+				path.EndpointB.ChannelID = ""
+				err := suite.chainB.App.GetScopedIBCKeeper().ReleaseCapability(suite.chainB.GetContext(), chanCap)
+				suite.Require().NoError(err)
+
+				suite.openAndCloseChannel(path)
+
+				// delete interchain account address
+				store := suite.chainB.GetContext().KVStore(suite.chainB.GetSimApp().GetKey(hosttypes.SubModuleName))
+				store.Delete(icatypes.KeyOwnerAccount(path.EndpointA.ChannelConfig.PortID, path.EndpointB.ConnectionID))
+
+				// assert interchain account address mapping was deleted
+				_, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				suite.Require().False(found)
 			}, true,
 		},
+		{
+			"reopening account fails - no existing account",
+			func() {
+				// create interchain account
+				// undo setup
+				path.EndpointB.ChannelID = ""
+				err := suite.chainB.App.GetScopedIBCKeeper().ReleaseCapability(suite.chainB.GetContext(), chanCap)
+				suite.Require().NoError(err)
+
+				suite.openAndCloseChannel(path)
+
+				// delete existing account
+				addr, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				suite.Require().True(found)
+
+				acc := suite.chainB.GetSimApp().AccountKeeper.GetAccount(suite.chainB.GetContext(), sdk.MustAccAddressFromBech32(addr))
+				suite.chainB.GetSimApp().AccountKeeper.RemoveAccount(suite.chainB.GetContext(), acc)
+			}, false,
+		},
+		{
+			"reopening account fails - existing account is not interchain account type",
+			func() {
+				// create interchain account
+				// undo setup
+				path.EndpointB.ChannelID = ""
+				err := suite.chainB.App.GetScopedIBCKeeper().ReleaseCapability(suite.chainB.GetContext(), chanCap)
+				suite.Require().NoError(err)
+
+				suite.openAndCloseChannel(path)
+
+				addr, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				suite.Require().True(found)
+
+				accAddress := sdk.MustAccAddressFromBech32(addr)
+				baseAcc := authtypes.NewBaseAccountWithAddress(accAddress)
+				suite.chainB.GetSimApp().AccountKeeper.SetAccount(suite.chainB.GetContext(), baseAcc)
+			}, false,
+		},
+		{
+			"account already exists",
+			func() {
+				interchainAccAddr := icatypes.GenerateAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				err := suite.chainB.GetSimApp().BankKeeper.SendCoins(suite.chainB.GetContext(), suite.chainB.SenderAccount.GetAddress(), interchainAccAddr, sdk.Coins{sdk.NewCoin("stake", sdk.NewInt(1))})
+				suite.Require().NoError(err)
+				suite.Require().True(suite.chainB.GetSimApp().AccountKeeper.HasAccount(suite.chainB.GetContext(), interchainAccAddr))
+			},
+			false,
+		},
 		{
 			"invalid metadata - previous metadata is different",
 			func() {
@@ -48,15 +144,17 @@ func (suite *KeeperTestSuite) TestOnChanOpenTry() {
 				suite.chainB.GetSimApp().GetIBCKeeper().ChannelKeeper.SetChannel(suite.chainB.GetContext(), path.EndpointB.ChannelConfig.PortID, path.EndpointB.ChannelID, ch)
 
 				// set the active channelID in state
-				suite.chainB.GetSimApp().ICAHostKeeper.SetActiveChannelID(suite.chainB.GetContext(), ibctesting.FirstConnectionID, path.EndpointA.ChannelConfig.PortID, path.EndpointB.ChannelID)
+				suite.chainB.GetSimApp().ICAHostKeeper.SetActiveChannelID(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID, path.EndpointB.ChannelID)
 
-				// modify metadata
+				// attempt to downgrade version by reinitializing channel with version 1, but setting channel to version 2
 				metadata.Version = "ics27-2"
 
 				versionBytes, err := icatypes.ModuleCdc.MarshalJSON(&metadata)
 				suite.Require().NoError(err)
 
-				path.EndpointA.ChannelConfig.Version = string(versionBytes)
+				channel.Version = string(versionBytes)
+
+				path.EndpointB.SetChannel(*channel)
 			}, false,
 		},
 		{
@@ -218,6 +316,16 @@ func (suite *KeeperTestSuite) TestOnChanOpenTry() {
 
 			if tc.expPass {
 				suite.Require().NoError(err)
+
+				storedAddr, found := suite.chainB.GetSimApp().ICAHostKeeper.GetInterchainAccountAddress(suite.chainB.GetContext(), path.EndpointB.ConnectionID, path.EndpointA.ChannelConfig.PortID)
+				suite.Require().True(found)
+
+				interchainAccAddr, err := sdk.AccAddressFromBech32(storedAddr)
+				suite.Require().NoError(err)
+
+				// Check if account is created
+				interchainAccount := suite.chainB.GetSimApp().AccountKeeper.GetAccount(suite.chainB.GetContext(), interchainAccAddr)
+				suite.Require().Equal(interchainAccount.GetAddress().String(), storedAddr)
 			} else {
 				suite.Require().Error(err)
 				suite.Require().Equal("", version)
```
