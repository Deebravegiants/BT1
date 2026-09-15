# [M] USDC amount that is accidentally sent to `EulerStrategy` contract cannot be transferred to `core` if admin of USDC blocks the relevant Euler's contract from sending USDC

## Summary
Severity: Medium
Reporter: rbserver
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L59-L73
Type: audit-issue

## Details
# USDC amount that is accidentally sent to `EulerStrategy` contract cannot be transferred to `core` if admin of USDC blocks the relevant Euler's contract from sending USDC

## Summary
If the admin of USDC adds the relevant Euler's contract address on USDC's blocklist, then the USDC amount that is accidentally sent to the `EulerStrategy` contract cannot be transferred to `core`.

## Vulnerability Detail
As shown in the Code Snippet section, the comment of the `EulerStrategy._withdrawAll` function mentions the possibility that some USDC amount could be sent to the `EulerStrategy` contract by accident. In this situation, the `EulerStrategy._withdrawAll` function can be called to transfer such USDC amount to `core` if `EUSDC.withdraw(SUB_ACCOUNT, type(uint256).max)` can be executed successfully. However, USDC includes a blocklist, and there is no guarantee that the admin of USDC will not block the relevant Euler's contract from sending USDC in the future. If this occurs, executing `EUSDC.withdraw(SUB_ACCOUNT, type(uint256).max)` will revert because the relevant Euler's contract is not allowed to send USDC, and then calling `EulerStrategy._withdrawAll` reverts. Similarly, calling `EulerStrategy._withdraw` will revert as well in this case.

## Impact
For the described scenario, because the USDC amount that is accidentally sent to the `EulerStrategy` contract cannot be transferred to `core`, the sender of such amount will lose that amount forever.

## Code Snippet
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L59-L73
```solidity
  function _withdrawAll() internal override returns (uint256 amount) {
    // If eUSDC.balanceOf(this) != 0, we can start to withdraw the eUSDC
    if (EUSDC.balanceOf(address(this)) != 0) {
      // Withdraw all underlying using max, this will translate to the full balance
      // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/BaseLogic.sol#L387
      EUSDC.withdraw(SUB_ACCOUNT, type(uint256).max);
    }

    // Amount of USDC in the contract
    // This can be >0 even if eUSDC balance = 0
    // As it could have been transferred to this contract by accident
    amount = want.balanceOf(address(this));
    // Transfer USDC to core
    if (amount != 0) want.safeTransfer(core, amount);
  }
```

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L77-L87
```solidity
  function _withdraw(uint256 _amount) internal override {
    // Don't allow to withdraw max (reserved with withdrawAll call)
    if (_amount == type(uint256).max) revert InvalidArg();

    // Call withdraw with underlying amount of tokens (USDC instead of eUSDC)
    // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol#L177
    EUSDC.withdraw(SUB_ACCOUNT, _amount);

    // Transfer USDC to core
    want.safeTransfer(core, _amount);
  }
```

## Tool used

Manual Review

## Recommendation
Another function that is similar to the `TrueFiStrategy._withdrawAll` function can be added in the `EulerStrategy` contract for only transferring the `EulerStrategy` contract's USDC balance to `core` without executing `EUSDC.withdraw(SUB_ACCOUNT, type(uint256).max)`.
