# [H] Locked assets in contracts

## Summary
Severity: High
Source: https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Comet.sol
Type: audit-issue

## Details
Once the protocol is deployed, the [Comet](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Comet.sol) and [Bulker](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Bulker.sol) contracts will be two important pieces of the system. `Comet` is the main protocol contract while the `Bulker` is a useful tool to execute multiple protocol calls into one single transaction.

For different purposes, both the `Comet` and the `Bulker` support deposits of ETH into the contract. In the case of the `Comet` contract, the [delegation](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Comet.sol#L1347) toward the `CometExt` is in the fallback function, which is declared as `payable`, but there are no parts of both contracts that use ether. Moreover, there is no direct way to withdraw any ETH balance present in the contract.

In the case of the `Bulker`, the contract has a [receive payable function](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Bulker.sol#L33) to accept ETH which is needed to be used in the `ACTION_WITHDRAW_ETH` according to the [docstrings](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Bulker.sol#L31). In this case, any ETH sent through the `receive` function will be again lost in the contract, with no possibility to upgrade to a new contract as the `Comet` can. The reason is that the `ACTION_WITHDRAW_ETH` is implemented into the [withdrawEthTo](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Bulker.sol#L108) function. This function unwraps WETH by sending tokens to the WETH contract and receiving back ETH in the same amount in the `Bulker` contract which are then sent to the user. In this case, the contract’s ETH balance will be untouched as only ETH coming from the unwrap will be used.

Lastly, a separate reference must also be done on ERC20 tokens. The `Comet` contract has the [approveThis](https://github.com/compound-finance/comet/blob/0f1221967149115f50a09681eea9580879ee7720/contracts/Comet.sol#L1294) function which is enough to let a `manager` move any ERC20 funds that might get lost in the `Comet` balance. However, this is not the case for the `Bulker` contract, where ERC20 tokens might also get lost.

Consider establishing mechanisms to avoid such scenarios, as it results in a direct loss of user funds.

**Update:** _Partially fixed in commit [3681613](https://github.com/compound-finance/comet/commit/36816138e15477d0ac487b9d97affc0d296ccc49). In the words of the team: “We think it’s a good idea to add sweep functions to the `Bulker` to prevent funds from being locked in there. As for `Comet`, we purposely made the `receive` function `payable` in case we ever wanted to support a `payable` function in `CometExt`. Doing so allows us to add a `payable` function to `CometExt` without having to also upgrade `Comet`. Since `Comet` is upgradeable, I don’t think we need to support a way to sweep ETH out of the contract right off the bat”._
