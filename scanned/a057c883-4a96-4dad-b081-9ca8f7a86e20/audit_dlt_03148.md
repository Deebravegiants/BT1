# [M] Lack of support for fee-on-transfer token

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-01-astaria
Published: 2023-01-09
Source: https://github.com/code-423n4/2023-01-astaria-findings/issues/51
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/TransferProxy.sol#L34
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/LienToken.sol#L181
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/LienToken.sol#L643


# Vulnerability details

## Impact
\
Lack of support for fee-on-transfer token.

## Proof of Concept

In the codebase, the usage of safeTransfer and safeTransferFrom assume that the receiver receive the exact transferred amount.

```solidity
src\AstariaRouter.sol:
  528      ERC20(IAstariaVaultBase(commitments[0].lienRequest.strategy.vault).asset())
  529:       .safeTransfer(msg.sender, totalBorrowed);
  530    }

src\ClearingHouse.sol:
  142  
  143:     ERC20(paymentToken).safeTransfer(
  144        s.auctionStack.liquidator,

  160      if (ERC20(paymentToken).balanceOf(address(this)) > 0) {
  161:       ERC20(paymentToken).safeTransfer(
  162          ASTARIA_ROUTER.COLLATERAL_TOKEN().ownerOf(collateralId),

src\PublicVault.sol:
  383  
  384:       ERC20(asset()).safeTransfer(currentWithdrawProxy, withdrawBalance);
  385        WithdrawProxy(currentWithdrawProxy).increaseWithdrawReserveReceived(

src\VaultImplementation.sol:
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-astaria-findings/issues/51_
