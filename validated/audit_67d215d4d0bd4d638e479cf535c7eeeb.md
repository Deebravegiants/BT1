### Title
No Recovery for Excess altRsETH Directly Transferred to `RsETHTokenWrapper` - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary
Any user can directly transfer an allowed altRsETH token to `RsETHTokenWrapper` without calling `deposit()`. Because no recovery function exists, those tokens are permanently frozen. The direct transfer also inflates `balanceOfAssetInWrapper` above `wrsETHSupply`, causing `maxAmountToDepositBridgerAsset()` to return `0` and blocking the bridger collateralization path used by every L2 pool contract.

### Finding Description
`RsETHTokenWrapper` tracks collateral implicitly via a live `balanceOf` call rather than an internal accounting variable.

`maxAmountToDepositBridgerAsset` computes the gap between outstanding wrsETH supply and the current altRsETH balance held by the wrapper:

```solidity
// contracts/L2/RsETHTokenWrapper.sol  lines 99-110
function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
    if (!allowedTokens[_asset]) return 0;

    uint256 wrsETHSupply = totalSupply();
    uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

    if (balanceOfAssetInWrapper > wrsETHSupply) return 0;   // ← collapses to 0

    return wrsETHSupply - balanceOfAssetInWrapper;
}
``` [1](#0-0) 

A standard ERC20 `transfer()` call to the wrapper address increases `balanceOfAssetInWrapper` without minting any wrsETH, so the condition `balanceOfAssetInWrapper > wrsETHSupply` becomes true and the function returns `0` permanently.

The contract has no `recoverTokens`, `rescue`, or equivalent function — the entire contract surface is: [2](#0-1) 

There is no path to retrieve tokens that arrive outside of `_deposit`. The same pattern is present in `AGETHTokenWrapper`: [3](#0-2) 

### Impact Explanation
**Critical — Permanent freezing of funds.**

Any altRsETH tokens sent directly to `RsETHTokenWrapper` are irrecoverable. There is no admin sweep, no `_recover` hook (unlike OpenZeppelin's `ERC20WrapperUpgradeable._recover`), and no `recoverTokens` utility (unlike `contracts/utils/Recoverable.sol`).

Secondary impact: once `maxAmountToDepositBridgerAsset` returns `0`, every pool contract that calls it (`RSETHPoolV2ExternalBridge`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) will revert on `swapAssetToPremintedRsETH` / `depositBridgerAssets` with `ExceedsMaxAmountToDepositInWrapper` / `CannotDeposit`, blocking the bridger collateralization flow until the imbalance is resolved — which it cannot be without a recovery function. [4](#0-3) 

### Likelihood Explanation
**Medium.** The entry path is a plain ERC20 `transfer()` call, requiring no special role. It can be triggered by:
- A user who mistakenly sends altRsETH to the wrapper address instead of calling `deposit()`.
- A griefing attacker who holds any amount of altRsETH and wants to permanently disable the bridger collateralization path.

The attacker needs only a dust amount of altRsETH to push `balanceOfAssetInWrapper` above `wrsETHSupply` (e.g., 1 wei if the wrapper is freshly deployed with zero supply).

### Recommendation
1. Add a `recoverExcessTokens(address asset, address recipient)` function restricted to `DEFAULT_ADMIN_ROLE` that transfers `balanceOf(asset) - totalSupply()` (for allowed tokens) or the full balance (for non-allowed tokens) to a designated recipient.
2. Alternatively, inherit or replicate the `_recover` pattern from OpenZeppelin's `ERC20WrapperUpgradeable`: [5](#0-4) 
3. Apply the same fix to `AGETHTokenWrapper`.

### Proof of Concept
```
State before:
  wrsETHSupply                = 1000e18
  altRsETH.balanceOf(wrapper) = 1000e18
  maxAmountToDepositBridgerAsset(altRsETH) = 0   (fully collateralized)

Attacker action:
  altRsETH.transfer(address(RsETHTokenWrapper), 1)   // plain ERC20 transfer, no role required

State after:
  wrsETHSupply                = 1000e18
  altRsETH.balanceOf(wrapper) = 1000e18 + 1
  maxAmountToDepositBridgerAsset(altRsETH) = 0   (balanceOfAssetInWrapper > wrsETHSupply → returns 0)

  The 1 wei is permanently frozen — no function in RsETHTokenWrapper can retrieve it.

  RSETHPoolV2ExternalBridge.swapAssetToPremintedRsETH(altRsETH, any_amount):
    → wrapper.maxAmountToDepositBridgerAsset(altRsETH) = 0
    → 0 < any_amount → revert ExceedsMaxAmountToDepositInWrapper
```

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L66-193)
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

    /// @notice Get the maximum amount of the bridged asset that can be deposited
    /// @param _asset The address of the token to deposit
    /// @return uint256
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrsETH minted
        uint256 wrsETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > wrsETHSupply) return 0;

        return wrsETHSupply - balanceOfAssetInWrapper;
    }

    /*//////////////////////////////////////////////////////////////
                           INTERNAL FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @dev Withdraw altRsETH tokens from wrsETH
    /// @param _asset The address of the token to withdraw
    /// @param _to The user to withdraw to
    /// @param _amount The amount of tokens to withdraw
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

    /// @notice Internal function to add a token to the allowed tokens list
    /// @param _asset The address of the token to add
    function _addAllowedToken(address _asset) internal {
        UtilLib.checkNonZeroAddress(_asset);
        if (allowedTokens[_asset]) revert TokenAlreadyAllowed();

        allowedTokens[_asset] = true;
        emit TokenAdded(_asset);
    }

    /*//////////////////////////////////////////////////////////////
                           RESTRICTED ACCESS FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @dev Legacy function - Deposit for when the rsETH is bridged by the
    /// bridger from L1 so as to collateralize already minted wrsETH on L2
    ///
    /// @param _asset The address of the token to deposit
    /// @param _amount The amount of tokens to deposit
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, msg.sender, _amount);
    }

    /// @dev Add a token to the allowed tokens list
    /// @param _asset The address of the token to add
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }

    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }

    /// @dev Mint wrsETH tokens on L2
    /// @param _to The address to mint the tokens to
    /// @param _amount The amount of tokens to mint
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
}
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L90-101)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrapped agETH minted
        uint256 agETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > agETHSupply) return 0;

        return agETHSupply - balanceOfAssetInWrapper;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L430-438)
```text
        if (!wrapper.allowedTokens(rsETH)) revert TokenNotAllowedInWrapper();
        if (rsETHAmount == 0) revert InvalidAmount();
        if (rsETHAmount > wrapper.maxAmountToDepositBridgerAsset(rsETH)) revert ExceedsMaxAmountToDepositInWrapper();

        // Get the amount of ETH to transfer to the user for the given amount of rsETH provided
        uint256 ethAmount = viewSwapAssetToPremintedRsETH(rsETHAmount);

        // Transfer rsETH from sender to the wrapper
        IERC20(rsETH).safeTransferFrom(msg.sender, address(wrapper), rsETHAmount);
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/extensions/ERC20WrapperUpgradeable.sol (L75-79)
```text
    function _recover(address account) internal virtual returns (uint256) {
        uint256 value = _underlying.balanceOf(address(this)) - totalSupply();
        _mint(account, value);
        return value;
    }
```
