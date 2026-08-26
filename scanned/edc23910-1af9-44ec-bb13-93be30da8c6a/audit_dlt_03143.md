# [H] Strategist can fail to withdraw asset token from a private vault

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-astaria
Published: 2023-01-19
Source: https://github.com/code-423n4/2023-01-astaria-findings/issues/489
Type: code-finding

## Details
# Lines of code

https://github.com/AstariaXYZ/astaria-gpl/blob/main/src/ERC4626RouterBase.sol#L41-L52
https://github.com/code-423n4/2023-01-astaria/blob/main/src/Vault.sol#L70-L73


# Vulnerability details

## Impact
Calling the `AstariaRouter.withdraw` function calls the following `ERC4626RouterBase.withdraw` function; however, calling `ERC4626RouterBase.withdraw` function for a private vault reverts because the `Vault` contract does not have an `approve` function. Directly calling the `Vault.withdraw` function for a private vault can also revert since the `Vault` contract does not have a way to set the allowance for itself to transfer the asset token, which can cause many ERC20 tokens' `transferFrom` function calls to revert when deducting the transfer amount from the allowance. Hence, after depositing some of the asset token in a private vault, the strategist can fail to withdraw this asset token from this private vault and lose this deposit.

https://github.com/AstariaXYZ/astaria-gpl/blob/main/src/ERC4626RouterBase.sol#L41-L52
```solidity
  function withdraw(
    IERC4626 vault,
    address to,
    uint256 amount,
    uint256 maxSharesOut
  ) public payable virtual override returns (uint256 sharesOut) {

    ERC20(address(vault)).safeApprove(address(vault), amount);
    if ((sharesOut = vault.withdraw(amount, to, msg.sender)) > maxSharesOut) {
      revert MaxSharesError();
    }
  }
```

https://github.com/code-423n4/2023-01-astaria/blob/main/src/Vault.sol#L70-L73
```solidity
  function withdraw(uint256 amount) external {
    require(msg.sender == owner());
    ERC20(asset()).safeTransferFrom(address(this), msg.sender, amount);
  }
```

## Proof of Concept
Please add the following test in `src\test\AstariaTest.t.sol`. This test will pass to demonstrate the described scenario.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-astaria-findings/issues/489_
