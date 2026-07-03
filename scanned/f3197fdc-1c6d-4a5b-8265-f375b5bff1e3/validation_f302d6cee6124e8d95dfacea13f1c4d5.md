### Title
Missing `_to != address(this)` Validation in `depositTo`/`withdrawTo` Causes Permanent Token Freeze - (File: contracts/agETH/AGETHTokenWrapper.sol)

### Summary
`AGETHTokenWrapper` exposes public `depositTo` and `withdrawTo` functions that accept a caller-controlled `_to` address. Neither the internal `_deposit` nor `_withdraw` function validates that `_to` is not the wrapper contract itself (`address(this)`). Passing the wrapper's own address as `_to` permanently freezes the deposited underlying tokens or the minted agETH inside the contract, with no recovery path.

### Finding Description
`depositTo` and `withdrawTo` are publicly callable by any user and forward the `_to` parameter directly to `_deposit` / `_withdraw` without any sanitization.

**`depositTo(asset, address(this), amount)` path:** [1](#0-0) 

`_deposit` is called, which transfers `amount` of the underlying alt-agETH from `msg.sender` into the wrapper, then mints `amount` of agETH **to `address(this)`** (the wrapper itself): [2](#0-1) 

The wrapper holds no logic to spend or transfer its own agETH balance. The minted agETH is permanently locked inside the contract, and the user's underlying tokens are irrecoverably collateralizing that locked supply.

**`withdrawTo(asset, address(this), amount)` path:** [3](#0-2) 

`_withdraw` burns `amount` of agETH from `msg.sender` and then transfers `amount` of the underlying alt-agETH **back to `address(this)`**: [4](#0-3) 

The underlying tokens re-enter the wrapper with no corresponding agETH supply increase. They are permanently stuck because there is no `_recover` function anywhere in the contract. [5](#0-4) 

The `maxAmountToDepositBridgerAsset` accounting is also corrupted: after a `withdrawTo(address(this))` call, `balanceOfAssetInWrapper > agETHSupply`, so the function returns 0 and the bridger can no longer deposit to rebalance: [6](#0-5) 

### Impact Explanation
**Critical — Permanent freezing of funds.**

- In the `depositTo` variant: the caller's underlying alt-agETH tokens are transferred into the wrapper and the minted agETH goes to the wrapper itself. Both are unrecoverable. The user suffers a total loss of the deposited amount.
- In the `withdrawTo` variant: the caller burns their agETH (permanent loss) and the underlying tokens are re-deposited into the wrapper with no owner, also unrecoverable.

There is no `_recover`, `sweep`, or admin-rescue function in `AGETHTokenWrapper`, so no privileged path exists to retrieve the stuck tokens.

### Likelihood Explanation
**Medium.** The functions are publicly callable with no access control. A user can trigger this accidentally (e.g., copy-pasting the wrapper contract address as the recipient) or a malicious actor can grief other users by front-running and redirecting their deposits. The entry path requires only a standard ERC20 `approve` + `depositTo` call sequence, which is the normal usage flow.

### Recommendation
Add a `require(_to != address(this), ...)` guard in both `_deposit` and `_withdraw`:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
+   require(_to != address(this), "AGETHTokenWrapper: cannot deposit to wrapper");
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);
    emit Deposit(_asset, _to, _amount);
}

function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
+   require(_to != address(this), "AGETHTokenWrapper: cannot withdraw to wrapper");
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, _to, _amount);
}
```

This mirrors the fix applied in OpenZeppelin's `ERC20Wrapper.depositFor`, which checks `sender != address(this)`: [7](#0-6) 

### Proof of Concept

```
Setup:
  - altAgETH token deployed, AGETHTokenWrapper deployed (wraps altAgETH 1:1)
  - Alice holds 100 altAgETH, approves AGETHTokenWrapper for 100

Attack (depositTo variant):
  1. Alice calls: wrapper.depositTo(altAgETH, address(wrapper), 100)
  2. _deposit executes:
       - altAgETH.transferFrom(Alice, wrapper, 100)  ✓ wrapper now holds 100 altAgETH
       - _mint(address(wrapper), 100)                ✓ wrapper now holds 100 agETH
  3. Alice has lost 100 altAgETH.
  4. wrapper.balanceOf(address(wrapper)) == 100  — no function can spend this
  5. No _recover() exists → tokens are permanently frozen.

Attack (withdrawTo variant):
  1. Bob holds 50 agETH (legitimately minted), calls:
       wrapper.withdrawTo(altAgETH, address(wrapper), 50)
  2. _withdraw executes:
       - _burn(Bob, 50)                              ✓ Bob loses 50 agETH
       - altAgETH.transfer(address(wrapper), 50)     ✓ wrapper gains 50 altAgETH with no new agETH minted
  3. Bob has lost 50 agETH AND 50 altAgETH are permanently frozen in the wrapper.
  4. maxAmountToDepositBridgerAsset now returns 0 (balanceOfAsset > agETHSupply),
     blocking the bridger rebalancing path.
```

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L1-168)
```text
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

import { AccessControlUpgradeable } from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {
    ERC20PermitUpgradeable
} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
import { ERC20Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import { SafeERC20Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";

/// @title AGETHTokenWrapper
/// @notice This contract is a wrapper for alternative agETH tokens in L2 chains for a canonical agETH token from Kelp
/// @dev It is an upgradeable ERC20 token that wraps an alternative agETH token
/// @dev It also uses the ERC20PermitUpgradeable extension
/// @dev The alt agETH tokens can be swapped 1:1 for the canonical agETH token
contract AGETHTokenWrapper is Initializable, AccessControlUpgradeable, ERC20Upgradeable, ERC20PermitUpgradeable {
    using SafeERC20Upgradeable for ERC20Upgradeable;

    bytes32 public constant MANAGER_ROLE = keccak256("MANAGER_ROLE");

    /// @dev The address of the alternative agETH token
    mapping(address allowedToken => bool isAllowed) public allowedTokens;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");

    error TokenNotAllowed();
    error CannotDeposit();

    event Deposit(address asset, address _sender, uint256 _amount);
    event Withdraw(address asset, address _sender, uint256 _amount);
    event BridgerDeposited(address asset, uint256 _amount);
    event TokenRemoved(address asset);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /// @dev Initialize the contract
    /// @param admin The address of the admin
    /// @param manager The address of the manager
    /// @param _altAgETH An alternative agETH token
    function initialize(address admin, address manager, address _altAgETH) external initializer {
        __ERC20_init("agETHWrapper", "agETH");
        __ERC20Permit_init("agETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(MANAGER_ROLE, manager);
        _setupRole(BRIDGER_ROLE, manager);

        allowedTokens[_altAgETH] = true;
    }

    /// @dev Deposit altAgETH for agETH
    /// @param asset The address of the token to deposit
    ///@param _amount The amount of tokens to deposit
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }

    /// @dev Deposit altAgETH for agETH to a user
    /// @param asset The address of the token to deposit
    /// @param _to The user to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function depositTo(address asset, address _to, uint256 _amount) external {
        _deposit(asset, _to, _amount);
    }

    /// @dev Withdraw altAgETH tokens from the contract
    /// @param asset The address of the token to withdraw
    /// @param _amount The amount of tokens to withdraw
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }

    /// @dev Withdraw altAgETH tokens from the contract to a user
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

        // get totalSupply of wrapped agETH minted
        uint256 agETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > agETHSupply) return 0;

        return agETHSupply - balanceOfAssetInWrapper;
    }

    /*//////////////////////////////////////////////////////////////
                           INTERNAL FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @dev Withdraw altAgETH tokens from the contract
    /// @param _asset The address of the token to withdraw
    /// @param _to The user to withdraw to
    /// @param _amount The amount of tokens to withdraw
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, _to, _amount);
    }

    /// @notice Deposit tokens into the lockbox
    /// @param _asset The address of the token to deposit
    /// @param _to The address to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
    }

    /*//////////////////////////////////////////////////////////////
                           RESTRICTED ACCESS FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @dev Legacy function - Deposit for when the agETH is bridged by the
    /// bridger from L1 so as to collateralize already minted agETH on L2
    ///
    /// @param _asset The address of the token to deposit
    /// @param _amount The amount of tokens to deposit
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, _amount);
    }

    /// Dont' allow to add other tokens at the moment. Only allow the altAgETH token as set in the initialize function

    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }

    /// @dev Mint agETH tokens on L2
    /// @param _to The address to mint the tokens to
    /// @param _amount The amount of tokens to mint
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
}
```

**File:** lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Wrapper.sol (L47-53)
```text
    function depositFor(address account, uint256 amount) public virtual returns (bool) {
        address sender = _msgSender();
        require(sender != address(this), "ERC20Wrapper: wrapper can't deposit");
        SafeERC20.safeTransferFrom(_underlying, sender, address(this), amount);
        _mint(account, amount);
        return true;
    }
```
