# [H] Tombstoned observer can maliciously add a duplicate observer address resulting in forfeiting voting rewards of targeted observers

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/411
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L36


# Vulnerability details

## Impact

1. If the `ObserverList` contains duplicates, any [newly created ballots will have duplicates in their `VoterList`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/keeper_utils.go#L74). As a result, this prevents an observer from receiving voting rewards as the reward for the legitimate vote would be offset by the [penalty received for missing the vote for the duplicate observer address](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/ballot.go#L88) ([repeatedly voting for a ballot with the same address does not work](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/ballot.go#L11)).
2. Removing an observer (e.g., due to the validator leaving the network or due to slashing) that has duplicates will only remove the first occurrence of the address in the list. See [node/x/observer/keeper/hooks.go#L142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/hooks.go#L142). The other occurrences will remain in the list and [allow](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/keeper_utils.go#L37) the observer to [continue to post new light-client block headers](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_add_block_header.go#L19).

## Proof of Concept

The `MsgUpdateObserver` message, handled in the [`UpdateObserver`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L12) function, allows the admin or an ([tombstoned](https://docs.cosmos.network/v0.45/modules/slashing/07_tombstone.html)) observer to update the observer address.

Internally, in line [`36`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L36), the [`UpdateObserverAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L86-L100) function is called to update the observer address in the `ObserverMapper` for each chain.

```go
086: func (k Keeper) UpdateObserverAddress(ctx sdk.Context, oldObserverAddress, newObserverAddress string) {
087: 	observerMappers := k.GetAllObserverMappers(ctx)
088: 	for _, om := range observerMappers {
089: 		UpdateObserverList(om.ObserverList, oldObserverAddress, newObserverAddress)
090: 		k.SetObserverMapper(ctx, om)
091: 	}
092: }
093:
094: func UpdateObserverList(list []string, oldObserverAddresss, newObserverAddress string) {
095: 	for i, observer := range list {
096: 		if observer == oldObserverAddresss {
097: 			list[i] = newObserverAddress
098: 		}
099: 	}
100: }
101:
```

However, a tombstoned observer is able to maliciously add a duplicate observer to the list by specifying an observer address (`NewObserverAddress`) in the `MsgUpdateObserver` message that is already in the `ObserverList` list.

As a result, the `ObserverList` list contains duplicates.

For the specific impact, please refer to the [Impact](#Impact) section.

### Test Case

The following test case demonstrates how the tombstoned `validator` can add a duplicate observer address:

<details>
  <summary><strong>Test case (click to reveal)</strong></summary>

```go
func TestAddDuplicateObserver(t *testing.T) {
	k, ctx := keepertest.ObserverKeeper(t)
	srv := keeper.NewMsgServerImpl(*k)
	// #nosec G404 test purpose - weak randomness is not an issue here
	r := rand.New(rand.NewSource(9))

	// Set validator in the store
	validator := sample.Validator(t, r)
	validatorOther := sample.Validator(t, r)
	validatorOther.Status = stakingtypes.Bonded
	validatorNew := sample.Validator(t, r)
	validatorNew.Status = stakingtypes.Bonded
	k.GetStakingKeeper().SetValidator(ctx, validatorNew)
	k.GetStakingKeeper().SetValidator(ctx, validator)
	k.GetStakingKeeper().SetValidator(ctx, validatorOther)

	consAddress, err := validator.GetConsAddr()
	assert.NoError(t, err)
	k.GetSlashingKeeper().SetValidatorSigningInfo(ctx, consAddress, slashingtypes.ValidatorSigningInfo{
		Address:             consAddress.String(),
		StartHeight:         0,
		JailedUntil:         ctx.BlockHeader().Time.Add(1000000 * time.Second),
		Tombstoned:          true,
		MissedBlocksCounter: 1,
	})

	chains := k.GetParams(ctx).GetSupportedChains()

	accAddressOfValidator, err := types.GetAccAddressFromOperatorAddress(validator.OperatorAddress)
	assert.NoError(t, err)

	accAddressOfOtherValidator, err := types.GetAccAddressFromOperatorAddress(validatorOther.OperatorAddress)
	assert.NoError(t, err)

	// newOperatorAddress, err := types.GetAccAddressFromOperatorAddress(validatorNew.OperatorAddress)
	// assert.NoError(t, err)

	count := uint64(0)
	for _, chain := range chains {
		k.SetObserverMapper(ctx, &types.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{accAddressOfValidator.String(), accAddressOfOtherValidator.String()},
		})
		count += 2
	}
	k.SetNodeAccount(ctx, types.NodeAccount{
		Operator: accAddressOfValidator.String(),
	})

	k.SetLastObserverCount(ctx, &types.LastObserverCount{
		Count: count,
	})

	_, err = srv.UpdateObserver(sdk.WrapSDKContext(ctx), &types.MsgUpdateObserver{
		Creator:            accAddressOfValidator.String(),
		OldObserverAddress: accAddressOfValidator.String(),
		NewObserverAddress: accAddressOfOtherValidator.String(),
		UpdateReason:       types.ObserverUpdateReason_Tombstoned,
	})
	assert.NoError(t, err)
	acc, found := k.GetNodeAccount(ctx, accAddressOfOtherValidator.String())
	assert.True(t, found)
	assert.Equal(t, accAddressOfOtherValidator.String(), acc.Operator)

	mapper, _ := k.GetObserverMapper(ctx, chains[0])

	assert.ElementsMatch(t, mapper.ObserverList, []string{accAddressOfOtherValidator.String(),   accAddressOfOtherValidator.String()}) // @audit-info Duplicate observers
}
```

**How to run this test case:**

Copy-pase the test case into `repos/node/x/observer/keeper/msg_server_update_observer_test.go` and run with `go test -v ./x/observer/keeper/msg_server_update_observer_test.go --run TestAddDuplicateObserver`

**Result:** The test will pass.

</details>

Please note that an admin can also accidentally add duplicate observers, [node/x/observer/keeper/msg_server_add_observer.go#L47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_add_observer.go#L47)

## Tools Used

Manual review

## Recommended mitigation steps

Consider checking in the [`UpdateObserverAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L86) function if the `newObserverAddress` is already in the list and return an error if it is.



## Assessed type

Invalid Validation
