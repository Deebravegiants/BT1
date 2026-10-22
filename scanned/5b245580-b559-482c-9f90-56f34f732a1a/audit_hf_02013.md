# [M] In `reimburseLiquidityFees`

## Summary
Severity: Medium
Contest weight: 0.5311
Dataset id: 11425
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[SponsorVault.sol#L187-L220](https://github.com/code-423n4/2022-06-connext/blob/b4532655071566b33c41eac46e75be29b4a381ed/contracts/contracts/core/connext/helpers/SponsorVault.sol#L187-L220)  

When code swaps tokens it should specify slippage but in `reimburseLiquidityFees()` code contract calls `tokenExchange.swapExactIn()` without slippage and it’s possible to perform sandwich attack and make contract to swap on bad exchange rates and there is MEV.

## Proof of Concept
This is `reimburseLiquidityFees()` code in `SponsorVault`:
```solidity
/**
 * @notice Performs liquidity fee reimbursement.
 * @dev Uses the token exchange or liquidity deposited in this contract.
 *      The `_receiver` address is only used for emitting in the event.
 * @param _token The address of the token
 * @param _liquidityFee The liquidity fee amount
 * @param _receiver The address of the receiver
 * @return Sponsored liquidity fee amount
 */
function reimburseLiquidityFees(
  address _token,
  uint256 _liquidityFee,
  address _receiver
) external override onlyConnext returns (uint256) {
  uint256 sponsoredFee;

  if (address(tokenExchanges[_token]) != address(0)) {
    uint256 currentBalance = address(this).balance;
    ITokenExchange tokenExchange = tokenExchanges[_token];

    uint256 amountIn = tokenExchange.getInGivenExpectedOut(_token, _liquidityFee);
    amountIn = currentBalance >= amountIn ? amountIn : currentBalance;

    // sponsored fee may end being less than _liquidityFee due to slippage
    sponsoredFee = tokenExchange.swapExactIn{value: amountIn}(_token, msg.sender);
  } else {
    uint256 balance = IERC20(_token).balanceOf(address(this));
    sponsoredFee = balance < _liquidityFee ? balance : _liquidityFee;

    // some ERC20 do not allow to transfer 0 amount
    if (sponsoredFee > 0) {
      IERC20(_token).safeTransfer(msg.sender, sponsoredFee);
    }
  }

  emit ReimburseLiquidityFees(_token, sponsoredFee, _receiver);

  return sponsoredFee;
}
```

As you can see there is no slippage defined when calling `swapExactIn()` can that swap could happen in any exchange rate. it’s possible to perform sandwich attack and do large swap before and after the transaction and make users lose funds. and it’s also MEV opportunity.

## Recommendation
Specify slippage when calling swap tokens.

This is absolutely correct, but unfortunately there is no apparent viable on-chain solution. If we revert because slippage is too high, behavior would be inconsistent and UX would be bad, to say the least. If we instead choose to _not sponsor_ because the slippage is too high, then sponsorship could be griefed severely (i.e. ‘if we can’t get at least X, then give the user nothing’ is not a valid sponsorship policy).

Some things that make a sandwich attack less feasible however:
  * Using exchanges with deep liquidity provision (sandwich attacks require principle liquidity, and cannot leverage flashloans).
  * The fact that the liquidity fee here is only .05% of the transfer means that it would take a very heavy-handed attack and at least 1 very large transfer to make it profitable (for a 1M transfer, max profit is 500 dollars).

This is a good entrypoint for a future feature that gives sponsors better options, such as only sponsoring transfers for specific assets that they supply (i.e. so no swap is required).

cc @LayneHaber for thoughts. Because this essentially boils down to a feature request on behalf of sponsors - not a bug.

Seeing as I can’t verify if `tokenExchange.swapExactIn` is indeed vulnerable to slippage, I will just side with the sponsor/warden on this one.
