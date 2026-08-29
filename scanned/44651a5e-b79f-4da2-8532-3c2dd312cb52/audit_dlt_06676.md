# [H] Missing Access Control on burnFrom() Function

## Summary
Severity: High
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/5
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/johny37)

  **Beneficiary:** 0x083A4CeA5cBF6dBFE8c6040787280d01D24aDDB9
  **Submission hash (on-chain):** 0x3dbebf3a0fa8cadddd0719c4319a66e546849032b2c196f10fec4ce7633a4fe1
  **Severity:** high
  
  **Description:**
  **Description**\

The ERC20Token contract overrides the burnFrom function without any allowance or access control checks. As implemented, burnFrom directly calls _burn(account, amount); without verifying that the caller is authorized to reduce account’s balance. This deviates from the typical OpenZeppelin ERC20Burnable pattern, where burnFrom first decreases the caller’s allowance and then burns on the holder’s behalf.

Impact: Any caller can burn tokens from any address, effectively destroying another user’s balance without the consent or an explicit allowance.

**Attack Scenario**\

Suppose Alice holds some tokens.
Malicious user (or even any user) calls tokenContract.burnFrom(Alice, x) with x > 0.
Since no allowance check or access control is in place, the function proceeds with _burn(Alice, x).
Alice’s balance is reduced by x, without her approval.

**Attachments**

1. **Revised Code File (Optional)**


Below is an example revision for ERC20Token.sol that reintroduces an allowance check inside burnFrom, matching the standard ERC20Burnable logic. Note that we remove the explicit override of burnFrom and let OpenZeppelin’s ERC20Burnable handle it, or we replicate the allowance logic if you require a custom version.

```solidity
/**
     * @notice Remove the custom override for burnFrom to rely on ERC20Burnable's
     *         built-in burnFrom, which checks allowance before burning:
     *
     *         function burnFrom(address account, uint256 amount) public virtual override {
     *             _spendAllowance(account, _msgSender(), amount);
     *             _burn(account, amount);
     *         }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/5_
