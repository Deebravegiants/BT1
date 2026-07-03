### Title
Same `wrsETH` Wrapper Token Used for All `allowedTokens` at 1:1 Regardless of Individual Token Value - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary

`RsETHTokenWrapper` allows any `allowedToken` to be deposited for `wrsETH` at a strict 1:1 ratio, and any `allowedToken` to be withdrawn by burning `wrsETH` at the same 1:1 ratio. When the wrapper holds multiple allowed altRsETH tokens with divergent market values, any user can deposit a lower-value altRsETH and immediately withdraw a higher-value altRsETH, stealing value from other depositors.

### Finding Description

`RsETHTokenWrapper` is designed to wrap multiple alternative rsETH tokens (bridged representations of rsETH on different L2s) into a single canonical `wrsETH` token. The contract supports multiple `allowedTokens` via `addAllowedToken` (TIMELOCK_ROLE) and `reinitialize`.

The internal `_deposit` function mints `wrsETH` 1:1 for any allowed token:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);          // always 1:1
    emit Deposit(_asset, msg.sender, _to, _amount);
}
```

The internal `_withdraw` function burns `wrsETH` and transfers any allowed token 1:1:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);   // always 1:1
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

Both `deposit` and `withdraw` are public with no access control:

```solidity
function deposit(address asset, uint256 _amount) external { _deposit(asset, msg.sender, _amount); }
function withdraw(address asset, uint256 _amount) external { _withdraw(asset, msg.sender, _amount); }
```

If `altRsETH_A` (e.g., a bridged rsETH from a chain where rsETH has depegged) trades at 0.90 ETH and `altRsETH_B` trades at 1.00 ETH, an attacker can:

1. Deposit `N` units of `altRsETH_A` → receive `N` `wrsETH` (1:1)
2. Withdraw `N` units of `altRsETH_B` → burn `N` `wrsETH` (1:1)
3. Net gain: `N × 0.10 ETH` at the expense of `altRsETH_B` holders in the wrapper

The wrapper's balance of `altRsETH_B` is drained, and the wrapper is left holding the depegged `altRsETH_A` instead. Legitimate users who deposited `altRsETH_B` and later try to withdraw it will find insufficient balance.

### Impact Explanation

**Critical — Direct theft of user funds.** Any user holding a lower-value allowed altRsETH token can drain the wrapper's balance of higher-value altRsETH tokens. The loss is borne by users who deposited the higher-value token. The wrapper's invariant (that `wrsETH` supply equals total altRsETH backing) is broken: the supply remains the same but the backing is now composed of devalued tokens.

### Likelihood Explanation

**Medium-High.** The wrapper explicitly supports multiple allowed tokens (the `addAllowedToken` function exists for this purpose, and `reinitialize` already adds a second token). Price divergence between different bridged representations of rsETH is a realistic market condition — bridging delays, chain-specific liquidity crises, or a depeg event on one chain would create the necessary spread. The attack requires no special role, no flash loan, and no complex setup beyond holding the lower-value altRsETH.

### Recommendation

The wrapper should either:
1. Restrict `withdraw` to only allow withdrawing the same token type that was deposited (track per-user per-token balances), or
2. Use a price oracle to enforce value-equivalent swaps between different allowed tokens rather than a flat 1:1 ratio, or
3. Limit the wrapper to a single canonical allowed token at any given time, preventing cross-token arbitrage.

### Proof of Concept

Assume `wrsETH` wrapper has two allowed tokens: `altRsETH_A` (depegged, worth 0.90 ETH) and `altRsETH_B` (canonical, worth 1.00 ETH). The wrapper holds 1000 `altRsETH_B` deposited by legitimate users.

```
Attacker holds: 1000 altRsETH_A (worth 900 ETH)
Wrapper holds:  1000 altRsETH_B (worth 1000 ETH)

Step 1: attacker.deposit(altRsETH_A, 1000)
  → wrapper receives 1000 altRsETH_A, mints 1000 wrsETH to attacker

Step 2: attacker.withdraw(altRsETH_B, 1000)
  → wrapper burns 1000 wrsETH, transfers 1000 altRsETH_B to attacker

Result:
  Attacker spent 900 ETH worth of altRsETH_A, received 1000 ETH worth of altRsETH_B
  Profit: 100 ETH
  Wrapper now holds 1000 altRsETH_A (worth 900 ETH) instead of 1000 altRsETH_B
  Legitimate altRsETH_B depositors cannot recover their full value
```

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L69-94)
```text
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }

    /// @dev Deposit altRsETH for wrsETH to a user
    /// @param asset The address of the token to deposit
    /// @param _to The user to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function depositTo(address asset, address _to, uint256 _amount) external {
        _deposit(asset, _to, _amount);
    }

    /// @dev Withdraw altRseth tokens from wrsETH
    /// @param asset The address of the token to withdraw
    /// @param _amount The amount of tokens to withdraw
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }

    /// @dev Withdraw altRsETH tokens from wrsETH to a user
    /// @param asset The address of the token to withdraw
    /// @param _to The user to withdraw to
    /// @param _amount The amount of tokens to withdraw
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L172-176)
```text
    /// @dev Add a token to the allowed tokens list
    /// @param _asset The address of the token to add
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }
```
