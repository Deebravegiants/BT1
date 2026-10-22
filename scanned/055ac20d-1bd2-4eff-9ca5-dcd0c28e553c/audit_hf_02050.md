# [M] Burnability of Locked Accounts

## Summary
Severity: Medium
Contest weight: 0.4294
Dataset id: 11678
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, both AUDT and DCAP are ERC20-compliant tokens. And the ERC20-compliance checks show that they are burnable, mintable, ownable, with the locking ability on a per-user basis. To elaborate, we show below the code snippet of ERC20Burnable. Note that both AUDT and DCAP token contracts directly inherit from ERC20Burnable. Although both AUDT and DCAP support the locking of a particular user, there is no locking-related validation checks in ERC20Burnable. As a result, the locked account may still be able to burn their tokens.
```solidity
abstract contract ERC20Burnable is Context, ERC20 {
    /**
     * @dev Destroys amount tokens from the caller.
     * See {ERC20-_burn}.
     */
    function burn(uint256 amount) public virtual {
        _burn(_msgSender(), amount);
    }

    /**
     * @dev Destroys amount tokens from account, deducting from the caller's
     * allowance.
     * See {ERC20-_burn} and {ERC20-allowance}.
     * Requirements:
     * - the caller must have allowance for accounts's tokens of at least
     * amount.
     */
    function burnFrom(address account, uint256 amount) public virtual {
        uint256 decreasedAllowance = allowance(account, _msgSender()).sub(amount, "ERC20: burn amount exceeds allowance");
        approve(account, _msgSender(), decreasedAllowance);
        _burn(account, amount);
    }
}
```

## Recommendation
Validate whether the account is being locked when burn() or burnFrom() is called. The burn operation should not proceed if the account is being locked.
