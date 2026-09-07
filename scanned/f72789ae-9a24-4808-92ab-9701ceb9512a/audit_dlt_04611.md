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
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/41_
