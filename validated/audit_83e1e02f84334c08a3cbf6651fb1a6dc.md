### Title
Fee-on-Transfer Token Mis-Accounting in Wrapper Deposit Causes Permanent Fund Freeze - (`contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

`RsETHTokenWrapper._deposit()` and `AGETHTokenWrapper._deposit()` mint exactly `_amount` of wrapper tokens after calling `safeTransferFrom(..., _amount)`, without measuring the actual tokens received. When an allowed token has a transfer fee, the contract receives fewer tokens than `_amount` but mints the full `_amount` of wrapper tokens, breaking the 1:1 backing invariant. The last withdrawers cannot redeem their wrapper tokens because the contract holds insufficient underlying assets.

---

### Finding Description

`RsETHTokenWrapper._deposit()` performs the following sequence:

```solidity
// contracts/L2/RsETHTokenWrapper.sol lines 134-141
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

    _mint(_to, _amount);   // <-- mints _amount, not actual received amount
    emit Deposit(_asset, msg.sender, _to, _amount);
}
``` [1](#0-0) 

If `_asset` is a fee-on-transfer token (e.g., 1% fee), a deposit of 1000 tokens results in only 990 tokens arriving at the contract, but 1000 wrsETH are minted. The contract's total wrsETH supply now exceeds its actual token holdings.

The `_withdraw()` function burns `_amount` wrsETH and then attempts to transfer `_amount` of the underlying token back to the user:

```solidity
// contracts/L2/RsETHTokenWrapper.sol lines 120-128
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    _burn(msg.sender, _amount);

    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);  // reverts if balance insufficient
    ...
}
``` [2](#0-1) 

Since the contract holds less underlying than the total wrsETH supply, the `safeTransfer` will revert for the last withdrawers once the deficit is reached. Their wrsETH is permanently frozen.

The identical pattern exists in `AGETHTokenWrapper._deposit()`: [3](#0-2) 

Additionally, `LRTDepositPool.depositAsset()` computes `rsethAmountToMint` from the caller-supplied `depositAmount` before the transfer, then mints rsETH based on that inflated figure rather than the actual received amount: [4](#0-3) 

---

### Impact Explanation

**Permanent freezing of funds (Critical).**

For `RsETHTokenWrapper`: every deposit of a fee-on-transfer token creates a shortfall equal to the fee amount. The shortfall accumulates across all deposits. When the aggregate shortfall exceeds the remaining underlying balance, subsequent `withdraw()` / `withdrawTo()` calls revert. The last holders of wrsETH cannot redeem their tokens — their funds are permanently frozen inside the wrapper.

For `LRTDepositPool.depositAsset()`: the depositor receives more rsETH than the protocol's actual TVL supports, diluting all existing rsETH holders and causing protocol insolvency proportional to the accumulated fee shortfall.

---

### Likelihood Explanation

**Medium.** The `RsETHTokenWrapper` supports multiple allowed tokens via `addAllowedToken()` (callable by `TIMELOCK_ROLE`). If any allowed token has a transfer fee (e.g., USDT in certain configurations, or any rebasing/fee token added in the future), every deposit through the public `deposit()` / `depositTo()` entry points triggers the mis-accounting. No special attacker capability is required — any ordinary depositor using a fee-on-transfer token triggers the bug. [5](#0-4) 

---

### Recommendation

In `_deposit()`, measure the actual received amount using a balance snapshot before and after the transfer, and mint only the received amount:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    uint256 balanceBefore = ERC20Upgradeable(_asset).balanceOf(address(this));
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    uint256 received = ERC20Upgradeable(_asset).balanceOf(address(this)) - balanceBefore;

    _mint(_to, received);   // mint only what was actually received
    emit Deposit(_asset, msg.sender, _to, received);
}
```

Apply the same fix to `AGETHTokenWrapper._deposit()` and to `LRTDepositPool.depositAsset()` (compute `rsethAmountToMint` from the actual received amount, not from `depositAmount`).

---

### Proof of Concept

1. Admin adds a fee-on-transfer token `FeeToken` (1% fee) as an allowed token in `RsETHTokenWrapper`.
2. Alice calls `deposit(FeeToken, 1000e18)`.
   - `safeTransferFrom` moves 1000 FeeToken from Alice; contract receives 990 FeeToken (1% fee taken).
   - `_mint(Alice, 1000e18)` — Alice holds 1000 wrsETH.
   - Contract holds 990 FeeToken but has 1000 wrsETH outstanding.
3. Bob calls `deposit(FeeToken, 1000e18)`.
   - Contract receives 990 FeeToken; mints 1000 wrsETH to Bob.
   - Contract now holds 1980 FeeToken, 2000 wrsETH outstanding. Shortfall = 20 FeeToken.
4. Alice calls `withdraw(FeeToken, 1000e18)`.
   - Burns 1000 wrsETH; transfers 1000 FeeToken to Alice. ✓ (1980 − 1000 = 980 remaining)
5. Bob calls `withdraw(FeeToken, 1000e18)`.
   - Burns 1000 wrsETH; attempts to transfer 1000 FeeToken — **reverts** (only 980 available).
   - Bob's 1000 wrsETH is permanently frozen.

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L66-79)
```text
    /// @dev Deposit altRsETH for wrsETH
    /// @param asset The address of the token to deposit
    ///@param _amount The amount of tokens to deposit
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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L125-132)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
    }
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```
