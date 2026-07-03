### Title
Fee-on-Transfer Token Causes Wrapper Over-Minting and Insolvency - (File: contracts/L2/RsETHTokenWrapper.sol, contracts/agETH/AGETHTokenWrapper.sol)

### Summary
Both `RsETHTokenWrapper` and `AGETHTokenWrapper` mint wrapper tokens 1:1 against the nominal `_amount` parameter rather than the actual tokens received. If a fee-on-transfer token is ever added to `allowedTokens`, the wrapper becomes undercollateralized: it mints more wrapper tokens than underlying tokens it holds, causing the last withdrawers to be unable to redeem their wrapper tokens.

### Finding Description
In `_deposit()`, the contract transfers `_amount` of the underlying token from the caller and immediately mints `_amount` wrapper tokens:

```solidity
// contracts/L2/RsETHTokenWrapper.sol, lines 137-139
ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
_mint(_to, _amount);
```

If the underlying token charges a transfer fee, the contract receives only `_amount - fee` tokens but mints `_amount` wrapper tokens. The invariant `totalSupply() == sum(balanceOf(underlying))` is broken from the first deposit.

In `_withdraw()`, the contract burns `_amount` wrapper tokens and attempts to transfer `_amount` underlying tokens back:

```solidity
// contracts/L2/RsETHTokenWrapper.sol, lines 123-125
_burn(msg.sender, _amount);
ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
```

Because the contract holds less than `totalSupply()` worth of underlying tokens, the last withdrawers will find the contract balance insufficient and their withdrawals will revert.

The identical pattern exists in `AGETHTokenWrapper._deposit()` and `AGETHTokenWrapper._withdraw()`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

Additionally, `maxAmountToDepositBridgerAsset()` computes `totalSupply() - balanceOf(address(this))` to cap bridger deposits. With fee-on-transfer tokens, `totalSupply()` exceeds `balanceOf(address(this))`, so this function returns an inflated cap, allowing the bridger to deposit even more collateral than needed — but the root insolvency is already baked in from user deposits. [5](#0-4) 

### Impact Explanation
Every deposit with a fee-on-transfer token mints more wrapper tokens than the contract can back. The shortfall accumulates with each deposit. When users attempt to withdraw, the contract's underlying token balance is insufficient to cover all outstanding wrapper tokens. The last users to withdraw have their funds permanently frozen inside the wrapper contract, as the `safeTransfer` call will revert due to insufficient balance. This constitutes **permanent freezing of funds** for a subset of users.

### Likelihood Explanation
The `addAllowedToken` function in `RsETHTokenWrapper` is callable by any address holding `TIMELOCK_ROLE`, and the `allowedTokens` mapping is open to any token address that passes the non-zero check. If any fee-on-transfer token (e.g., a rebasing or taxed bridge token) is ever whitelisted — even accidentally — the vulnerability is immediately exploitable by any depositor calling the public `deposit()` or `depositTo()` functions. No special privileges are required to trigger the insolvency once a fee-on-transfer token is allowed. [6](#0-5) 

### Recommendation
Measure the actual received amount using a before/after balance check and mint only that amount:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    uint256 balanceBefore = ERC20Upgradeable(_asset).balanceOf(address(this));
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    uint256 actualReceived = ERC20Upgradeable(_asset).balanceOf(address(this)) - balanceBefore;

    _mint(_to, actualReceived);
    emit Deposit(_asset, msg.sender, _to, actualReceived);
}
```

Apply the same fix to `AGETHTokenWrapper._deposit()`.

### Proof of Concept
1. A fee-on-transfer token `FeeToken` (1% fee) is added to `allowedTokens` in `RsETHTokenWrapper`.
2. Alice calls `deposit(FeeToken, 1000e18)`.
   - Contract receives `990e18` FeeToken (1% fee deducted).
   - Contract mints `1000e18` wrsETH to Alice.
3. Bob calls `deposit(FeeToken, 1000e18)`.
   - Contract receives `990e18` FeeToken.
   - Contract mints `1000e18` wrsETH to Bob.
4. Contract state: `totalSupply() = 2000e18` wrsETH, `FeeToken.balanceOf(wrapper) = 1980e18`.
5. Alice calls `withdraw(FeeToken, 1000e18)`:
   - Burns `1000e18` wrsETH. ✓
   - Transfers `1000e18` FeeToken to Alice. ✓ (contract now holds `980e18`)
6. Bob calls `withdraw(FeeToken, 1000e18)`:
   - Burns `1000e18` wrsETH. ✓
   - Attempts to transfer `1000e18` FeeToken — **reverts**, contract only holds `980e18`.
   - Bob's `20e18` FeeToken worth of value is permanently frozen. [1](#0-0) [3](#0-2)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L99-110)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrsETH minted
        uint256 wrsETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > wrsETHSupply) return 0;

        return wrsETHSupply - balanceOfAssetInWrapper;
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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-119)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, _to, _amount);
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
