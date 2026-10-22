# [M] Canceled event not emitted

## Summary
Severity: Medium
Source: https://github.com/ripio/marmo-contracts/blob/d3fb5922a4f01e47d585343d08cccfad659b3584/contracts/Marmo.sol#L13
Type: audit-issue

## Details
The `Marmo` contract has a [Canceled](https://github.com/ripio/marmo-contracts/blob/d3fb5922a4f01e47d585343d08cccfad659b3584/contracts/Marmo.sol#L13) event that should be emitted when an intent is canceled. However, this event is not emitted by the [cancel](https://github.com/ripio/marmo-contracts/blob/d3fb5922a4f01e47d585343d08cccfad659b3584/contracts/Marmo.sol#L131) function. This will make more difficult for clients to follow the status of intents, forcing them to either listen for all the transactions of the contract or to poll calling [isCanceled](https://github.com/ripio/marmo-contracts/blob/d3fb5922a4f01e47d585343d08cccfad659b3584/contracts/Marmo.sol#L58).

Consider emitting `Canceled` at the end of the `cancel` function.

**_Update:_** _Fixed in_ [_pull request #29_](https://github.com/ripio/marmo-contracts/pull/29/files)_._
