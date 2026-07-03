### Title
Missing `_to` Address Validation in `withdrawTo` Enables Permanent User Fund Loss - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary
`RsETHTokenWrapper.withdrawTo` and `AGETHTokenWrapper.withdrawTo` accept an arbitrary `_to` address with no validation. A user who passes the wrapper contract's own address as `_to` will have their wrsETH/agETH permanently burned while the underlying altRsETH/altAgETH is locked in the contract with no recovery path.

### Finding Description
`withdrawTo` is a permissionless function callable by any wrsETH holder. It delegates to `_withdraw(asset, _to, _amount)`:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);                                    // wrsETH burned first
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);          // then altRsETH sent to _to
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

There is no validation on `_to`. While `address(0)` is incidentally protected — OpenZeppelin's `safeTransfer` reverts on zero-address, rolling back the entire transaction including the burn — passing `address(this)` (the wrapper contract itself) succeeds completely: the burn executes, and the altRsETH is transferred into the contract. The `RsETHTokenWrapper` contract has no `recoverTokens`, `sweep`, or equivalent function, so the altRsETH is irrecoverable by the original user. The identical pattern exists in `AGETHTokenWrapper._withdraw`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The same missing check applies to `depositTo`: if `_to = address(this)`, the user's altRsETH is pulled in and wrsETH is minted to the contract itself — permanently locked since the contract has no self-calling withdraw path. [5](#0-4) [6](#0-5) 

### Impact Explanation
The user's wrsETH is permanently burned and the underlying altRsETH is sent to the contract with no on-chain recovery mechanism. From the user's perspective this is a permanent, irreversible loss of funds. The contract contains no `recoverTokens` or admin sweep function for the altRsETH asset. [2](#0-1) 

### Likelihood Explanation
Low. The user must explicitly supply the contract address as `_to` — a realistic copy-paste or UI confusion error (e.g., pasting the wrapper contract address instead of a personal wallet), directly analogous to the BitVMBridge case where a user supplies a malformed destination string. No privileged role or attacker is required; any wrsETH holder can trigger this against themselves.

### Recommendation
Add a self-address and zero-address guard in `_withdraw` (and symmetrically in `_deposit`) for both `RsETHTokenWrapper` and `AGETHTokenWrapper`:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    if (_to == address(0) || _to == address(this)) revert InvalidRecipient();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

### Proof of Concept
1. User holds 100e18 wrsETH and calls `withdrawTo(altRsETH, address(wrsETHWrapper), 100e18)`.
2. `_withdraw` is entered with `_to = address(wrsETHWrapper)`.
3. `_burn(msg.sender, 100e18)` executes — user's wrsETH is gone.
4. `ERC20Upgradeable(altRsETH).safeTransfer(address(wrsETHWrapper), 100e18)` executes — altRsETH is deposited back into the wrapper contract.
5. No recovery function exists in `RsETHTokenWrapper`; the user has permanently lost 100e18 wrsETH worth of value with no recourse. [2](#0-1) [4](#0-3)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L77-79)
```text
    function depositTo(address asset, address _to, uint256 _amount) external {
        _deposit(asset, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L92-94)
```text
    function withdrawTo(address asset, address _to, uint256 _amount) external {
        _withdraw(asset, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L83-85)
```text
    function withdrawTo(address asset, address _to, uint256 _amount) external {
        _withdraw(asset, _to, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-119)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, _to, _amount);
    }
```
