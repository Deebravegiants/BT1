### Title
Removing an Allowed Token in `RsETHTokenWrapper` Permanently Traps User Deposits - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary

`RsETHTokenWrapper` allows users to deposit an `altRsETH` token in exchange for `wrsETH` (minted 1:1). The only redemption path back to the underlying `altRsETH` is `_withdraw()`, which hard-gates on `allowedTokens[_asset]`. A privileged `TIMELOCK_ROLE` holder can call `removeAllowedToken()` to set that flag to `false`. Once removed, every user who deposited that token is permanently unable to redeem their `wrsETH` for the underlying asset, because no emergency-exit path exists for users.

### Finding Description

`RsETHTokenWrapper` maintains an `allowedTokens` mapping that gates both deposit and withdrawal paths:

```solidity
// contracts/L2/RsETHTokenWrapper.sol
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();   // line 121
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

The `TIMELOCK_ROLE` can remove any token from the allowed list:

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    allowedTokens[_asset] = false;          // line 183
    emit TokenRemoved(_asset);
}
```

After `removeAllowedToken(altRsETH)` is called:

- `withdraw(altRsETH, amount)` reverts with `TokenNotAllowed` for every holder.
- `withdrawTo(altRsETH, to, amount)` reverts identically.
- There is no admin-callable rescue function that transfers the locked `altRsETH` back to depositors.
- The `wrsETH` ERC-20 tokens remain transferable but are unbacked — the underlying `altRsETH` is stranded inside the wrapper contract.

The most realistic trigger is a token migration: the operator removes the old `altRsETH` address and adds a new one. Any user who has not yet called `withdraw` before the removal is executed loses access to their underlying tokens. Because `addAllowedToken` requires `TIMELOCK_ROLE` and a separate governance action, re-adding the token is not guaranteed, and even if re-added, a window of inaccessibility exists.

### Impact Explanation

All `altRsETH` tokens deposited by users who have not yet withdrawn are locked inside `RsETHTokenWrapper` with no user-accessible exit. The `wrsETH` they hold becomes worthless for redemption of that specific underlying asset. This constitutes **permanent freezing of user funds** if the token is not re-added, or **temporary freezing** during any migration window.

### Likelihood Explanation

Token migrations (e.g., upgrading from one bridge-wrapped rsETH variant to another) are a normal operational event for a multi-chain protocol. The M-07 report explicitly identifies this as the most likely trigger. No attacker action is required — a routine governance call is sufficient. The `TIMELOCK_ROLE` is a protocol-controlled role, not an external attacker, making this an operational risk rather than an external exploit, but the fund-freeze impact on users is identical.

### Recommendation

1. Add a user-accessible emergency withdrawal path that bypasses the `allowedTokens` check when the contract holds a balance of the requested token, so users can always recover their own deposits regardless of the token's allowed status.
2. Alternatively, before calling `removeAllowedToken`, require that the contract's balance of that token is zero (i.e., all users have already withdrawn), preventing removal while user funds remain.
3. At minimum, emit a time-delayed event or enforce a timelock delay before a removal takes effect, giving users time to withdraw before the gate closes.

### Proof of Concept

1. Alice calls `deposit(altRsETH, 100e18)` → wrapper holds 100 `altRsETH`, Alice holds 100 `wrsETH`. [1](#0-0) 

2. `TIMELOCK_ROLE` calls `removeAllowedToken(altRsETH)` → `allowedTokens[altRsETH] = false`. [2](#0-1) 

3. Alice calls `withdraw(altRsETH, 100e18)` → `_withdraw` checks `allowedTokens[altRsETH]` → `false` → reverts `TokenNotAllowed`. [3](#0-2) 

4. Alice's 100 `altRsETH` remain locked in the wrapper. Her `wrsETH` cannot be burned for any value. No function in the contract allows her to recover the underlying tokens. [4](#0-3)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L1-193)
```text
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

import { SafeERC20Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import { ERC20Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import {
    ERC20PermitUpgradeable
} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
import { AccessControlUpgradeable } from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

import { UtilLib } from "contracts/utils/UtilLib.sol";

/// @title RsETHTokenWrapper
/// @notice This contract is a wrapper for alternative RsETH tokens in L2 chains from a canonical rsETH token for
/// KelpDao
/// @dev it is an upgradeable ERC20 token that wraps an alternative RsETH token
/// It also uses the ERC20PermitUpgradeable extension
/// the alt rsETH tokens can be swapped 1:1 for the canonical rsETH token
contract RsETHTokenWrapper is Initializable, AccessControlUpgradeable, ERC20Upgradeable, ERC20PermitUpgradeable {
    using SafeERC20Upgradeable for ERC20Upgradeable;

    /// @dev The address of the alternative RsETH token
    mapping(address allowedToken => bool isAllowed) public allowedTokens;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    error TokenNotAllowed();
    error TokenAlreadyAllowed();
    error CannotDeposit();

    event Deposit(address indexed asset, address indexed sender, address indexed receiver, uint256 amount);
    event Withdraw(address indexed asset, address indexed sender, address indexed receiver, uint256 amount);
    event BridgerDeposited(address indexed asset, address indexed bridger, uint256 amount);
    event TokenAdded(address indexed asset);
    event TokenRemoved(address indexed asset);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /// @dev Reinitialize the contract
    /// @param _altRsETH An alternative RsETH token
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }

    /// @dev Initialize the contract
    /// @param admin The address of the admin
    /// @param bridger The address of the bridger
    /// @param _altRsETH An alternative RsETH token
    function initialize(address admin, address bridger, address _altRsETH) external initializer {
        __ERC20_init("rsETHWrapper", "wrsETH");
        __ERC20Permit_init("rsETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        _addAllowedToken(_altRsETH);
    }

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
