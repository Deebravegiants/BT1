# [M] FeeBuyback submit may end up being blocked for some ERC20

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L68-L73
Type: audit-issue

## Details
# FeeBuyback submit may end up being blocked for some ERC20

## Summary

Some tokens (USDT on mainnet as an example) do not allow to approve positive value when approval is already positive. This can cause permanent DOS if not handled beforehand.

## Vulnerability Detail

FeeBuyback#submit() approves positive amount while previous approval for the same token can not be used fully yet, thus having a possibility to find itself in the situation of trying to approve positive value when the allowance is neither max, nor zero. In this cases the corresponding tokens will enter reverting state, i.e. revert all similar calls, and, as this function is the only way to use the allowance, disable submit() functionality for that token.

## Impact

submit() can become permanently unavailable for such ERC20, which can lead to losses for wallet owners who depend on the usage of this token. Say submit() can be integrated to the automatic workflow and its unavailability will lead to not doing a swap when it's needed, which is partial loss of principal kind of impact. Setting the severity to medium due to preconditions.

## Code Snippet

submit() approves the `amount` needed for 1inch right away:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L68-L73

```solidity
    //MATIC does not allow for approvals
    //ERC20s only
    if (token != MATIC) {
      IERC20(token).transferFrom(_safe, address(this), amount);
      IERC20(token).approve(_aggregator, amount);
    }
```

Depending on the type of the swap the allowance may not be used fully:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L75-L82

```solidity
    //Perform secondary swap from fee token to TEL
    //do simple transfer from and submit
    (bool swapResult,) = _aggregator.call{value: msg.value}(swapData);
    require(swapResult, "FeeBuyback: swap transaction failed");
    _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
    require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
    return true;
  }
```

If it wasn't and submit() called again with the same token, which doesn't allow positive approval with the allowance being already positive (to fight the race conditions), the submit() become unavailable for the token. 

## Tool used

Manual Review

## Recommendation

Consider unifying approval logic by clearing it first, for example: 

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L68-L73

```solidity
    //MATIC does not allow for approvals
    //ERC20s only
    if (token != MATIC) {
      IERC20(token).transferFrom(_safe, address(this), amount);
+     IERC20(token).approve(_aggregator, 0);
      IERC20(token).approve(_aggregator, amount);
    }
```
