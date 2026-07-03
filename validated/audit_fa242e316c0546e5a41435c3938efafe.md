### Title
Fee-on-Transfer Token Causes Wrapper to Mint More Shares Than Tokens Received - (File: contracts/L2/RsETHTokenWrapper.sol, contracts/agETH/AGETHTokenWrapper.sol)

### Summary
Both `RsETHTokenWrapper._deposit` and `AGETHTokenWrapper._deposit` mint wrapper tokens 1:1 based on the caller-supplied `_amount` parameter, without verifying that the actual tokens received equal `_amount`. If a fee-on-transfer token is added as an allowed asset, the contract mints more wrapper tokens than underlying tokens it holds, creating unbacked supply and enabling theft of other depositors' funds.

### Finding Description
In `RsETHTokenWrapper._deposit` (and the identical pattern in `AGETHTokenWrapper._deposit`):

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

    _mint(_to, _amount);  // mints _amount, not actual received amount
    emit Deposit(_asset, msg.sender, _to, _amount);
}
```

The contract calls `safeTransferFrom` with `_amount` and then immediately mints exactly `_amount` of wrapper tokens to `_to`. There is no balance-before/balance-after check to determine the actual number of tokens received. If the underlying `_asset` is a fee-on-transfer token (e.g., one that deducts a 1% transfer fee), the contract receives `_amount * 0.99` but mints `_amount` wrapper tokens — creating `_amount * 0.01` unbacked wrapper tokens per deposit.

The `_withdraw` function burns exactly `_amount` wrapper tokens and transfers exactly `_amount` underlying tokens back:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    ...
}
```

This means the contract will eventually be unable to honor all withdrawals — the last withdrawers will find the contract insolvent.

The `allowedTokens` mapping is open to any token added via `addAllowedToken` (gated by `TIMELOCK_ROLE`) or set during `initialize`. The design explicitly supports multiple allowed tokens (the mapping is `mapping(address allowedToken => bool isAllowed)`), meaning a fee-on-transfer variant of an alt-rsETH or alt-agETH token could be added.

The analog to the original report is exact: the code checks only that `safeTransferFrom` does not revert (i.e., received > 0 implicitly), rather than verifying `received == _amount`.

### Impact Explanation
**Critical / High.** Any user who deposits a fee-on-transfer allowed token receives more `wrsETH` (or `agETH` wrapper) than the contract holds in underlying collateral. These excess wrapper tokens can be redeemed against the pool's reserves funded by other honest depositors. The last withdrawers cannot redeem their wrapper tokens for the full underlying amount — direct theft of other depositors' underlying assets. This is a share/asset mis-accounting leading to protocol insolvency for the wrapper pool.

### Likelihood Explanation
Medium. The `allowedTokens` mechanism is explicitly designed to support multiple alt-rsETH/alt-agETH tokens. If any such token implements a transfer fee (common in rebasing or bridged token variants), the vulnerability is immediately exploitable by any unprivileged depositor calling `deposit(asset, amount)` or `depositTo(asset, to, amount)` — both are public with no access control.

### Recommendation
Use a balance-before/balance-after pattern to determine the actual received amount, and mint only that amount:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    uint256 balanceBefore = ERC20Upgradeable(_asset).balanceOf(address(this));
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    uint256 received = ERC20Upgradeable(_asset).balanceOf(address(this)) - balanceBefore;

    _mint(_to, received);
    emit Deposit(_asset, msg.sender, _to, received);
}
```

Apply the same fix to `AGETHTokenWrapper._deposit`.

### Proof of Concept

1. Admin adds a fee-on-transfer alt-rsETH token (1% fee) via `addAllowedToken`.
2. Attacker calls `deposit(feeToken, 1000e18)`.
   - Contract receives `990e18` tokens (after 1% fee).
   - Contract mints `1000e18` wrsETH to attacker.
3. Honest user calls `deposit(feeToken, 1000e18)`.
   - Contract receives `990e18` tokens.
   - Contract mints `1000e18` wrsETH to honest user.
   - Contract now holds `1980e18` underlying but has `2000e18` wrsETH outstanding.
4. Attacker calls `withdraw(feeToken, 1000e18)`.
   - Burns `1000e18` wrsETH, receives `1000e18` underlying tokens (another fee deducted from recipient, but attacker still drains more than they deposited net of fees).
   - Contract now holds `980e18` underlying but `1000e18` wrsETH outstanding for the honest user.
5. Honest user calls `withdraw(feeToken, 1000e18)` — reverts or receives less than deposited, losing funds.

Root cause lines: [1](#0-0) [2](#0-1)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L137-139)
```text
        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L128-130)
```text
        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
```
