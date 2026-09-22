# [M] Non-USDC ERC20 tokens, which are accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract, cannot be transferred to `core`

## Summary
Severity: Medium
Reporter: rbserver
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L59-L73
Type: audit-issue

## Details
# Non-USDC ERC20 tokens, which are accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract, cannot be transferred to `core`

## Summary
The ERC20 tokens, which are not USDC, that are accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract cannot be transferred to `core`.

## Vulnerability Detail
As shown in the Code Snippet section, calling the `EulerStrategy._withdrawAll`, `EulerStrategy._withdraw`, `TrueFiStrategy._withdrawAll`, and `TrueFiStrategy._withdraw` functions can transfer the corresponding amounts of `want` to `core`. Because `want` is specified to be USDC, it is not possible to transfer any non-USDC ERC20 tokens to `core` that are accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract.

## Impact
Since these ERC20 tokens, which are not USDC, that are accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract cannot be transferred to `core`, the senders who accidentally sent them cannot get them back and would lose them forever.

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

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L109-L114
```solidity
  function _withdrawAll() internal override returns (uint256 amount) {
    // Amount of USDC in the contract
    amount = want.balanceOf(address(this));
    // Transfer USDC to core
    if (amount != 0) want.safeTransfer(core, amount);
  }
```

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L119-L122
```solidity
  function _withdraw(uint256 _amount) internal override {
    // Transfer USDC to core
    want.safeTransfer(core, _amount);
  }
```

## Tool used

Manual Review

## Recommendation
In each of the `EulerStrategy` and `TrueFiStrategy` contracts, a function can be added for transferring the contract's balance of a specified ERC20 token, which is not USDC, to `core`.
