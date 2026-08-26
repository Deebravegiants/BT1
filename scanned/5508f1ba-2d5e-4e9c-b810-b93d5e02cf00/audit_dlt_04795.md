# [M] The yield distributor can transfer accidentally sent funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/41
Type: sherlock-finding

## Details
berndartmueller

medium

# The yield distributor can transfer accidentally sent funds

## Summary

The yield distributor can repurpose the `claimFees` function to transfer accidentally sent funds to itself.

## Vulnerability Detail

Both the `ExchangeProxy` and `HardenedTopupProxy` contracts have a function `emergencyTransfer` to allow an admin to rescue any ERC20 tokens accidentally sent to the contracts.

However, a yield distributor can also transfer those funds via the `claimFees` function. The `claimFees` function is intended to be used by the yield distributor to claim collected fees. As the contracts do not keep track of the fees collected, the yield distributor is able to claim and transfer any amount of ERC-20 tokens and native tokens, effectively stealing funds.

## Impact

The yield distributor can transfer any ERC-20 tokens and native tokens accidentally sent to the contracts besides the fees collected.

## Code Snippet

[ExchangeProxy.sol#L242-L263](https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L242-L263)

```solidity
function claimFees(address _token, uint256 _amount) public {
    require(msg.sender == yieldDistributorAddress, "yield distributor only");
    if (_token != ETH_TOKEN_ADDRESS) {
        IERC20(_token).safeTransfer(msg.sender, _amount);
    } else {
        payable(msg.sender).sendValue(_amount);
    }
}

/**
    @dev all contracts that do not hold funds have this emergency function if someone occasionally
      transfers ERC20 tokens directly to this contract
      callable only by owner (admin)
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/41_
