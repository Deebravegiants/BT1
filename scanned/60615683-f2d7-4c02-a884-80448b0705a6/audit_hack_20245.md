# [M] 5.2.18 Pulling tokens byLibSwap.swap()is counterintuitive

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LibSwap.sol#L30-L68, SwapperV2.sol#L67-L81, Swapper.sol#L65-L78, Executor.sol#L323-L333
**Description:** The functionLibSwap.swap()pulls in tokens viatransferFromERC20()frommsg.senderwhen
needed. When put in a loop, via_executeSwaps(), it can pull in multiple different tokens. It also doesn’t detect
accidentally sending of native tokens withERC20tokens. This approach is counterintuitive and leads to risks.
Suppose someone wants to swap 100 USDC to 100 DAI and then 100 DAI to 100 USDT. If the first swap somehow
gives back less tokens, for example 90 DAI, thenLibSwap.swap()pulls in 10 extra DAI frommsg.sender. Note:
this requires themsg.senderhaving given multiple allowances to the LiFi Diamond.
Another risk is that an attacker tricks a user to sign a transaction for the LiFi protocol. Within one transaction it
can sweep multiple tokens from the user, cleaning out his entire wallet. Note: this requires themsg.senderhaving
given multiple allowances to the LiFi Diamond.
InExecutor.solthe tokens are already deposited, so the "pull" functionality is not needed and can even result
in additional issues. InExecutor.solit tries to "pull" tokens from "msg.sender" itself. In the best case of ERC20
implementations (like OpenZeppeling, Solmate) this has no effect. However some non standard ERC20 imple-
mentations might break.


```
contract SwapperV2 is ILiFi {
function _executeSwaps(...) ... {
...
for (uint256 i = 0; i < _swapData.length; i++) {
...
LibSwap.swap(_lifiData.transactionId, currentSwapData);
}
}
}
library LibSwap {
function swap(...) ... {
...
uint256 initialSendingAssetBalance = LibAsset.getOwnBalance(fromAssetId);
...
uint256 toDeposit = initialSendingAssetBalance < fromAmount? fromAmount -
,! initialSendingAssetBalance : 0;
...
if (toDeposit != 0) {
LibAsset.transferFromERC20(fromAssetId, msg.sender, address(this), toDeposit);
}
}
}
```
**Recommendation:** In Swapper.sol/ SwapperV2.sol: Use LibAsset.depositAsset() before doing
_executeSwaps()/_executeAndCheckSwaps(). This also prevent accidentally sending native tokens with ERC20
tokens (asLibAsset.depositAsset()checksmsg.value).
Change functionswap()to something like this:
library LibSwap {
function swap(...) ... {
...

- uint256 toDeposit = initialSendingAssetBalance < fromAmount? fromAmount -
    ,! initialSendingAssetBalance : 0;
+ if (initialSendingAssetBalance < fromAmount) revert NotEnoughFunds();
    ...
- if (toDeposit != 0) {
- LibAsset.transferFromERC20(fromAssetId, msg.sender, address(this), toDeposit);
- }
    }
}

This will also make sure_executeSwapsofExecutor.soldoesn’t pull any tokens.
Alternatively at least change the names to something like this:

- LibSwap.swap()==>LibSwap.pullTokensAndSwap().
- _executeSwaps()==>_pullTokensAndExecuteSwaps()(3 locations).
- _executeAndCheckSwaps==>_pullTokensAndExecuteAndCheckSwaps(3 locations).
And consider adding anemitoftoDeposit.
**LiFi:** Fixed with PR #94 & PR #96.
**Spearbit:** Verified.
