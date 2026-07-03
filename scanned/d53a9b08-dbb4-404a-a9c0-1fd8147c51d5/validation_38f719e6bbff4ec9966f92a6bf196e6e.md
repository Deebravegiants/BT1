### Title
Cross-Asset Withdrawal Allows Theft of Higher-Value Tokens from Wrapper - (File: contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

`RsETHTokenWrapper` supports multiple allowed alt-rsETH tokens. Because `_deposit` and `_withdraw` track only the user's `wrsETH` balance (via ERC20 mint/burn) and not *which specific asset* was deposited, any holder of `wrsETH` can withdraw any allowed asset regardless of which asset they originally deposited. If two allowed tokens temporarily diverge in value, an attacker can deposit the cheaper token and withdraw the more valuable one, draining it from honest depositors.

---

### Finding Description

`RsETHTokenWrapper` maintains a mapping `allowedTokens` that can hold multiple alt-rsETH token addresses, added via `addAllowedToken` (restricted to `TIMELOCK_ROLE`). The `_deposit` internal function accepts any allowed asset, transfers it in, and mints an equal number of `wrsETH` tokens. The `_withdraw` internal function accepts any allowed asset, burns `wrsETH`, and transfers the requested asset out.

```solidity
// contracts/L2/RsETHTokenWrapper.sol
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);                          // mints wrsETH, no record of which asset
    emit Deposit(_asset, msg.sender, _to, _amount);
}

function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);                   // burns wrsETH, no check on original deposit asset
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

There is no `mapping(depositor => asset)` or any other bookkeeping that ties a user's `wrsETH` balance to the specific asset they deposited. The only invariant enforced is that the caller holds enough `wrsETH` to burn. This is the direct analog of the Bribes.sol pattern: deposit to target A, withdraw from target B. [1](#0-0) 

---

### Impact Explanation

**Impact: Critical — Direct theft of user funds.**

When two allowed tokens trade at different prices (e.g., one alt-rsETH depegs to 0.95 while the other remains at 1.00), an attacker can:

1. Acquire the cheaper token (tokenA) at market price.
2. Call `deposit(tokenA, N)` → receives N `wrsETH`.
3. Call `withdraw(tokenB, N)` → burns N `wrsETH`, receives N tokenB (worth more).

The attacker extracts the price difference from the pool of tokenB deposited by honest users. The honest users who deposited tokenB are left holding `wrsETH` that can only be redeemed for the now-depleted tokenB balance, or must accept the cheaper tokenA instead. [2](#0-1) 

---

### Likelihood Explanation

**Likelihood: Medium.**

- The `TIMELOCK_ROLE` can add a second allowed token at any time via `addAllowedToken`. The contract is explicitly designed to support multiple alt-rsETH tokens (the mapping is `allowedTokens`, plural, and the `reinitialize` function adds a second token).
- Alt-rsETH tokens on different L2 chains are bridge-wrapped representations that can and do temporarily depeg during bridge congestion, liquidity crises, or oracle delays.
- The attack requires no privileged access once a second token is listed; any unprivileged user holding `wrsETH` or the cheaper alt-rsETH can execute it atomically. [3](#0-2) [4](#0-3) 

---

### Recommendation

Track which asset each unit of `wrsETH` was minted against, and enforce that withdrawals use the same asset:

```solidity
// Short term: per-user per-asset deposit accounting
mapping(address user => mapping(address asset => uint256 amount)) public depositedAsset;

function _deposit(address _asset, address _to, uint256 _amount) internal {
    ...
    depositedAsset[_to][_asset] += _amount;
    _mint(_to, _amount);
}

function _withdraw(address _asset, address _to, uint256 _amount) internal {
    require(depositedAsset[msg.sender][_asset] >= _amount, "wrong asset");
    depositedAsset[msg.sender][_asset] -= _amount;
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
}
```

Alternatively, issue separate wrapper tokens per allowed asset (one `wrsETH-tokenA`, one `wrsETH-tokenB`) so that cross-asset redemption is structurally impossible.

---

### Proof of Concept

Precondition: `TIMELOCK_ROLE` has called `addAllowedToken(tokenB)` so both `tokenA` and `tokenB` are allowed. `tokenA` trades at 0.95 ETH, `tokenB` at 1.00 ETH. The wrapper holds 1000 `tokenB` deposited by honest users.

```
1. Attacker buys 100 tokenA for 95 ETH on the open market.
2. Attacker calls: wrapper.deposit(tokenA, 100)
   → wrapper receives 100 tokenA, mints 100 wrsETH to attacker.
3. Attacker calls: wrapper.withdraw(tokenB, 100)
   → wrapper burns 100 wrsETH, transfers 100 tokenB to attacker.
4. Attacker sells 100 tokenB for 100 ETH.
   Net profit: 5 ETH. Honest tokenB depositors are short 100 tokenB.
```

The `_withdraw` function at line 120–128 performs no check that `_asset` matches the asset originally deposited; it only verifies `allowedTokens[_asset]` and that the caller holds sufficient `wrsETH`. [5](#0-4)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L47-49)
```text
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L84-94)
```text
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-141)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }

    /// @notice Deposit tokens into the lockbox
    /// @param _asset The address of the token to deposit
    /// @param _to The address to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
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
