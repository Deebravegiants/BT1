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

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/411_
