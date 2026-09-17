# [M] Possible index out of range in GetVoterIndex could cause ballot to never finalize due to panic

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-11-27
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/116
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L27-L35


# Vulnerability details

## Description
The function `GetVoterIndex` is used in multiple places to get the index of a specific Observer from the Voter List. The problem is that the caller is assuming the function will always succeed, but clearly there is a possibility where the `Observer address could not be found`, which would return an `index of -1`, which will effectivelly make the program panic.


```golang
func (m Ballot) GetVoterIndex(address string) int {
	index := -1
	for i, addr := range m.VoterList {
		if addr == address {
			return i
		}
	}
	return index
}
```

#### **[Instance 1]**
##### `Observer::BallotByIdentifier`
This one is safe since the GetVoterIndex is called from the same ballot instance it is iterating over, so it's impossible to not find the index in such case.
```golang
	for i, voterAddress := range ballot.VoterList {
		voter := types.VoterList{
			VoterAddress: voterAddress,
			VoteType:     ballot.Votes[ballot.GetVoterIndex(voterAddress)],
		}
		votersList[i] = &voter
	}
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/ballot.go#L94


#### **[Instance 2]**
##### `Observer::BuildRewardsDistribution`
Safe, for the same reason as instance 1.
```golang
		for _, address := range m.VoterList {
			vote := m.Votes[m.GetVoterIndex(address)]
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L82
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L92

#### **[Instance 3]**
##### `Observer::HasVoted`
Even if this is public function, it's actually a private one and only used by `AddVote`, so share the same risk.
```golang
func (m Ballot) HasVoted(address string) bool {
	index := m.GetVoterIndex(address)
	return m.Votes[index] != VoteType_NotYetVoted
}
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L22

#### **[Instance 4]**
##### `Observer::AddVote`
This is the `spicy one` which has some risks. This is called by [AddVoteToBallot](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/keeper_utils.go#L12) which is then called in `6 differents places` ([VoteOnObservedInboundTx](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L95), [VoteOnObservedOutboundTx](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L105), [CreateTSSVoter 1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L69), [CreateTSSVoter 2](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L74), [AddBlameVote](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_blame_vote.go#L39) and [AddBlockHeader](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_block_header.go#L79)), with the ballot instance and address being looked at coming in different parameters and from different sources, so here there is posibility the issue could occur.
```golang
func (m Ballot) AddVote(address string, vote VoteType) (Ballot, error) {
	if m.HasVoted(address) {
		return m, errors.Wrap(ErrUnableToAddVote, fmt.Sprintf(" Voter : %s | Ballot :%s | Already Voted", address, m.String()))
	}
	// `index` is the index of the `address` in the `VoterList`
	// `index` is used to set the vote in the `Votes` array
	index := m.GetVoterIndex(address)
	m.Votes[index] = vote
	return m, nil
}
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L16



## Impact
- `zetaclientd` would panic (so crash) if the indicated code path is activated in **Instance 4**.
- The ballot created and still in progress `might never be able to be finalized` depending on how many Observer have been updated and what is the threshold. A ballot never finalizing would mean the CCTX never reaching consensus and funds loss, which is why this seems to warrant `High` severity.

## Proof of Concept
Here is a PoC when using `AddBlockHeader`, but there might be other cracks coming from the 5 other places I identified for **Instance 4** where this code path can be activated.

1) `AddBlockHeader` gRPC endpoint is called by Observer A. Current Observer list is A,B. Since this is the first vote, the ballot is created by `FindBallot` with observers list being A,B.
2) Afterward, `UpdateObserver` gRPC endpoint is called to update Observer B for reason `ObserverUpdateReason_AdminUpdate`. This update Observer B address to now be C in the the `ObserverMapper` and the observer list.
3) `AddBlockHeader` is called by Observer C (which was previously B). The ballot created previously is retrieved and `AddVoteToBallot` is called, which in turns call `ballot.AddVote(C,...)`, which in turns call `HasVoted` which will **panic** against `return m.Votes[index] != VoteType_NotYetVoted` since index will be **-1**, as C is not in the ballot Observer list.
```
	// AddVoteToBallot adds a vote and sets the ballot
	ballot, err = k.AddVoteToBallot(ctx, ballot, vote.Creator, types.VoteType_SuccessObservation)
	if err != nil {
		return nil, err
	}
```
```
func (m Ballot) AddVote(address string, vote VoteType) (Ballot, error) {
	if m.HasVoted(address) {
		return m, errors.Wrap(ErrUnableToAddVote, fmt.Sprintf(" Voter : %s | Ballot :%s | Already Voted", address, m.String()))
	}
```
```
func (m Ballot) HasVoted(address string) bool {
	index := m.GetVoterIndex(address)
	return m.Votes[index] != VoteType_NotYetVoted
}
```

## Coded PoC
In order to demostrate my point explained before, I coded it in the following unit test. With the original code it will panic, while by adding my recommendation it will not and recover.
```
func TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver(t *testing.T) {
	header, _, _, err := sample.EthHeader()
	assert.NoError(t, err)
	header1RLP, err := rlp.EncodeToBytes(header)
	assert.NoError(t, err)

	observerChain := common.GoerliChain()
	r := rand.New(rand.NewSource(9))
	validatorA := sample.Validator(t, r)
	validatorB := sample.Validator(t, r)
	validatorC := sample.Validator(t, r)
	observerAddressA, _ := types.GetAccAddressFromOperatorAddress(validatorA.OperatorAddress)
	observerAddressB, _ := types.GetAccAddressFromOperatorAddress(validatorB.OperatorAddress)
	observerAddressC, _ := types.GetAccAddressFromOperatorAddress(validatorC.OperatorAddress)

	tt := []struct {
		name                  string
		msg                   *types.MsgAddBlockHeader
		msg1                  *types.MsgAddBlockHeader
		IsEthTypeChainEnabled bool
		IsBtcTypeChainEnabled bool
		validatorA            stakingtypes.Validator
		validatorB            stakingtypes.Validator
	}{
		{
			name: "success submit eth header",
			msg: &types.MsgAddBlockHeader{
				Creator:   observerAddressA.String(),
				ChainId:   common.GoerliChain().ChainId,
				BlockHash: header.Hash().Bytes(),
				Height:    1,
				Header:    common.NewEthereumHeader(header1RLP),
			},
			msg1: &types.MsgAddBlockHeader{
				Creator:   observerAddressC.String(),
				ChainId:   common.GoerliChain().ChainId,
				BlockHash: header.Hash().Bytes(),
				Height:    1,
				Header:    common.NewEthereumHeader(header1RLP),
			},
			IsEthTypeChainEnabled: true,
			IsBtcTypeChainEnabled: true,
			validatorA:            validatorA,
			validatorB:            validatorB,
		},
	}
	for _, tc := range tt {
		t.Run(tc.name, func(t *testing.T) {
			k, ctx := keepertest.ObserverKeeper(t)
			srv := keeper.NewMsgServerImpl(*k)
			k.SetObserverMapper(ctx, &types.ObserverMapper{
				ObserverChain: &observerChain,
				ObserverList:  []string{observerAddressA.String(), observerAddressB.String()},
			})
			k.GetStakingKeeper().SetValidator(ctx, tc.validatorA)
			k.GetStakingKeeper().SetValidator(ctx, tc.validatorB)

			k.SetCrosschainFlags(ctx, types.CrosschainFlags{
				IsInboundEnabled:      true,
				IsOutboundEnabled:     true,
				GasPriceIncreaseFlags: nil,
				BlockHeaderVerificationFlags: &types.BlockHeaderVerificationFlags{
					IsEthTypeChainEnabled: tc.IsEthTypeChainEnabled,
					IsBtcTypeChainEnabled: tc.IsBtcTypeChainEnabled,
				},
			})

			// First vote for BlockHeader with ObserverA which will create the ballot as first voter
			// Voterlist in the ballot struct: A,B
			_, err := srv.AddBlockHeader(ctx, tc.msg)

			// Setup such that UpdateObserver is happy
			admin := sample.AccAddress()
			validatorC.Status = stakingtypes.Bonded
			k.GetStakingKeeper().SetValidator(ctx, validatorC)
			setAdminCrossChainFlags(ctx, k, admin, types.Policy_Type_group2)

			k.SetNodeAccount(ctx, types.NodeAccount{
				Operator: observerAddressB.String(),
			})
			k.SetLastObserverCount(ctx, &types.LastObserverCount{
				Count: 2,
			})

			// Observer: B --> C
			_, err = srv.UpdateObserver(ctx, &types.MsgUpdateObserver{
				Creator:            admin,
				OldObserverAddress: observerAddressB.String(),
				NewObserverAddress: observerAddressC.String(),
				UpdateReason:       types.ObserverUpdateReason_AdminUpdate,
			})

			// Second vote for BlockHeader with ObserverC, that was before ObserverB. This will panic
			_, err = srv.AddBlockHeader(ctx, tc.msg1)
			assert.NotNil(t, err)
		})
	}
}
```
#### Call stack
```
=== RUN   TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver
--- FAIL: TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver (0.56s)
=== RUN   TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver/success_submit_eth_header
    --- FAIL: TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver/success_submit_eth_header (0.02s)
panic: runtime error: index out of range [-1] [recovered]
	panic: runtime error: index out of range [-1]

goroutine 98 [running]:
testing.tRunner.func1.2({0x168aea0, 0xc0006a6c00})
	/usr/local/go/src/testing/testing.go:1526 +0x24e
testing.tRunner.func1()
	/usr/local/go/src/testing/testing.go:1529 +0x39f
panic({0x168aea0, 0xc0006a6c00})
	/usr/local/go/src/runtime/panic.go:884 +0x213
github.com/zeta-chain/zetacore/x/observer/types.Ballot.HasVoted(...)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/types/ballot.go:28
github.com/zeta-chain/zetacore/x/observer/types.Ballot.AddVote({{0xc00025d8b0, 0x42}, {0xc00025d900, 0x42}, {0xc0013d36a0, 0x2, 0x2}, {0xc0013022e0, 0x2, 0x2}, ...}, ...)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/types/ballot.go:11 +0x4b9
github.com/zeta-chain/zetacore/x/observer/keeper.Keeper.AddVoteToBallot({{0x1bd0ac0, 0xc000c9e410}, {0x1bb7050, 0xc000d51540}, {0x1bb7078, 0xc000d51550}, {{0x1bd0ac0, 0xc000c9e410}, 0xc000014b50, {0x1bb7050, ...}, ...}, ...}, ...)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/keeper/keeper_utils.go:13 +0x10f
github.com/zeta-chain/zetacore/x/observer/keeper.msgServer.AddBlockHeader({{{0x1bd0ac0, 0xc000c9e410}, {0x1bb7050, 0xc000d51540}, {0x1bb7078, 0xc000d51550}, {{0x1bd0ac0, 0xc000c9e410}, 0xc000014b50, {0x1bb7050, ...}, ...}, ...}}, ...)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/keeper/msg_server_add_block_header.go:79 +0x906
github.com/zeta-chain/zetacore/x/observer/keeper_test.TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver.func1(0xc0010104e0?)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/keeper/msg_server_add_block_header_test.go:267 +0xd48
testing.tRunner(0xc0010104e0, 0xc00066e000)
	/usr/local/go/src/testing/testing.go:1576 +0x10b
created by testing.(*T).Run
	/usr/local/go/src/testing/testing.go:1629 +0x3ea


Process finished with the exit code 1
```

## Recommended Mitigation Steps
The probability of the indicated negative impacts happening as soon as `UpdateObserver` is pretty high depending on the blockchain activity (and ballot currently in progress), but calling `UpdateObserver` should not happen often and can only be triggered by the `Admins Group2` (multi-sig).

Granted that the scenario exposed in my PoC might be rare, I haven't taken the time to investigate all the other coner cases where this code path can be activated, which raise doubts on the frequency such scenario can happen which is another reason why it should be mitigated.

I would recommend todo the following changes in order to fix the panic in `HasVoted` and `AddVote` at least which seems to present some risks. That will not resolve the issue that impacted ballot might never been able to finalize. A way to mitigate this would be to update also the ballot when updating the observer address.

```diff
diff --git a/repos/node/x/observer/types/ballot.go b/repos/node/x/observer/types/ballot.go
index dae3476..1e44221 100644
--- a/repos/node/x/observer/types/ballot.go
+++ b/repos/node/x/observer/types/ballot.go
@@ -14,13 +14,20 @@ func (m Ballot) AddVote(address string, vote VoteType) (Ballot, error) {
        // `index` is the index of the `address` in the `VoterList`
        // `index` is used to set the vote in the `Votes` array
        index := m.GetVoterIndex(address)
-       m.Votes[index] = vote
-       return m, nil
+       if index != -1 {
+               m.Votes[index] = vote
+               return m, nil
+       }
+
+       return m, errors.Wrap(ErrUnableToAddVote, fmt.Sprintf(" Voter : %s | Ballot :%s | Not found!", address, m.String()))
 }

 func (m Ballot) HasVoted(address string) bool {
        index := m.GetVoterIndex(address)
-       return m.Votes[index] != VoteType_NotYetVoted
+       if index != -1 {
+               return m.Votes[index] != VoteType_NotYetVoted
+       }
+       return false
 }
```





















































## Assessed type

Invalid Validation
