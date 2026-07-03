### Title
`burnFrom` Requires Allowance Despite `onlyBurner` Guard, Inconsistent with `burn(uint256)` — (`contracts/ccip/WrappedRSETH.sol`)

### Summary
`WrappedRSETH` exposes two burn paths gated by `onlyBurner`. `burn(uint256)` burns from `msg.sender` directly with no allowance check, while `burnFrom(address,uint256)` delegates to `ERC20Burnable.burnFrom`, which calls `_spendAllowance(account, msg.sender, amount)` and reverts if the account has not pre-approved the caller. A registered burner calling `burnFrom(self, amount)` will always revert without a prior self-approval, even though the role check already authorizes the operation.

### Finding Description

`WrappedRSETH` inherits `ERC20Burnable` and overrides both burn entry points:

```solidity
// contracts/ccip/WrappedRSETH.sol:115-117
function burn(uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
    super.burn(amount);   // → _burn(msg.sender, amount)  — no allowance check
}
``` [1](#0-0) 

```solidity
// contracts/ccip/WrappedRSETH.sol:129-131
function burnFrom(address account, uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
    super.burnFrom(account, amount);  // → _spendAllowance(account, msg.sender, amount) → revert if no allowance
}
``` [2](#0-1) 

`ERC20Burnable.burnFrom` unconditionally calls `_spendAllowance`:

```solidity
// lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol:35-38
function burnFrom(address account, uint256 amount) public virtual {
    _spendAllowance(account, _msgSender(), amount);
    _burn(account, amount);
}
``` [3](#0-2) 

The `burn(address,uint256)` alias also routes through `burnFrom`, inheriting the same defect:

```solidity
// contracts/ccip/WrappedRSETH.sol:122-124
function burn(address account, uint256 amount) public virtual override {
    burnFrom(account, amount);
}
``` [4](#0-3) 

The `IBurnMintERC20` interface documents `burnFrom` as "Burns tokens from a given address" with no mention of an allowance prerequisite, implying the burner role alone is sufficient authorization. [5](#0-4) 

### Impact Explanation
A CCIP pool or any registered burner that holds wrsETH and calls `burnFrom(self, amount)` will receive `ERC20InsufficientAllowance` without a prior `approve(self, amount)`. `burn(amount)` succeeds for the identical operation. This creates an inconsistent API surface: the contract fails to deliver the behavior promised by the `IBurnMintERC20` interface and the `onlyBurner` role abstraction, though no funds are lost. Impact: **Low — contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation
Any CCIP pool integration that follows the `IBurnMintERC20` interface and calls `burnFrom(poolAddress, amount)` (a common pattern in Chainlink CCIP token pool implementations) will hit this revert. The path is reachable without any privileged compromise — only a registered burner role is required, which is the intended caller.

### Recommendation
Override `burnFrom` to bypass the allowance check when the caller is a registered burner burning from their own address, or implement a custom `_burnFrom` that calls `_burn` directly after the `onlyBurner` check:

```solidity
function burnFrom(address account, uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
    _burn(account, amount);
}
```

This aligns the behavior with `burn(uint256)` and the interface's documented semantics.

### Proof of Concept
1. Deploy `WrappedRSETH`.
2. Grant burner role to address `A`.
3. Mint tokens to `A`.
4. Call `A.burn(amount)` → succeeds.
5. Mint tokens to `A` again.
6. Call `A.burnFrom(A, amount)` **without** `A.approve(A, amount)` → reverts with `ERC20InsufficientAllowance`.
7. Call `A.approve(A, amount)` then `A.burnFrom(A, amount)` → succeeds, confirming the self-approval workaround.

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L115-117)
```text
    function burn(uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
        super.burn(amount);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L122-124)
```text
    function burn(address account, uint256 amount) public virtual override {
        burnFrom(account, amount);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L129-131)
```text
    function burnFrom(address account, uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
        super.burnFrom(account, amount);
    }
```

**File:** lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol (L35-38)
```text
    function burnFrom(address account, uint256 amount) public virtual {
        _spendAllowance(account, _msgSender(), amount);
        _burn(account, amount);
    }
```

**File:** contracts/ccip/IBurnMintERC20.sol (L24-28)
```text
    /// @notice Burns tokens from a given address..
    /// @param account The address to burn tokens from.
    /// @param amount The number of tokens to be burned.
    /// @dev this function decreases the total supply.
    function burnFrom(address account, uint256 amount) external;
```
