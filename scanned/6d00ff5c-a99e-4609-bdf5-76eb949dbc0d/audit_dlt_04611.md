# [M] Malicious executor or owner can drain all safe funds using FeeBuyback

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/41
Type: sherlock-finding

## Details
rvierdiiev

medium

# Malicious executor or owner can drain all safe funds using FeeBuyback

## Summary
Malicious executor can drain all funds from safe with fake transaction and rescueERC20 function.
## Vulnerability Detail
Function FeeBuyback.submit should be callable by owner.
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47-L82
```solidity
  function submit(address wallet, bytes memory walletData, address token, address recipient, uint256 amount, bytes memory swapData) external override payable onlyOwner() returns (bool) {
    //Perform user swap first
    //Verify success
    (bool walletResult,) = wallet.call{value: 0}(walletData);
    require(walletResult, "FeeBuyback: wallet transaction failed");


    //check if this is a referral transaction
    //if not exit execution
    if (token == address(0) || recipient == address(0) || amount == 0 ) {
      return false;
    }


    //if swapped token is in TEL, no swap is necessary
    //do simple transfer from and submit
    if (token == address(_telcoin)) {
      _telcoin.transferFrom(_safe, address(this), amount);
      _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
      require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
      return true;
    }


    //MATIC does not allow for approvals
    //ERC20s only
    if (token != MATIC) {
      IERC20(token).transferFrom(_safe, address(this), amount);
      IERC20(token).approve(_aggregator, amount);
    }


    //Perform secondary swap from fee token to TEL
    //do simple transfer from and submit
    (bool swapResult,) = _aggregator.call{value: msg.value}(swapData);
    require(swapResult, "FeeBuyback: swap transaction failed");
    _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
    require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
    return true;
  }
```
When token param is provided to submit function then the provided amount is transferred from safe to FeeBuyback. After that 1inch swap is called that should swap all sent funds from safe to FeeBuyback to TEL token. And after that TEL is sent to plugin.

Attack scenario.
1.Safe contains big amount of TOKEN_X.
2.Malicious executor makes himself an owner(or another account) using TieredOwnership.addOwner function.
3.Malicious executor(from owner account) calls submit and provides TOKEN_X and full amount of TOKEN_X that is controlled by safe.
4.Also he provides swapData param to 1inch that will transfer some small amount of MATIC token(was provided as msg.value) to TEL token.
5.After execution FeeBuyback controlls all amount of safe's TOKEN_X and they were not sent to plugin.
6.Executor calls rescueERC20 function and receives money.

Also same thing can be done by owner.
1.Safe contains big amount of TOKEN_X.
2.Malicious owner sends small amount of TEL token to FeeBuyback.
3.Malicious owner calls submit and provides TOKEN_X and full amount of TOKEN_X that is controlled by safe.
4.Also he provides swapData param to 1inch that will swap full amount of TOKEN_X token for any other token and will transfer that swapped funds to owner's account.
4.After execution small amount of TEL that was sent by owner was sent to plugin and all amount of TOKEN_X is sent to owner account.
## Impact
Executor or owner steals tokens from safe.
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47-L82
## Tool used

Manual Review

## Recommendation
Check that provided token balance of FeeBuyback is 0 after swap and revert if not or send back to safe.
