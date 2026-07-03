### Title
Bridge-minted wrsETH Drains deposit()-path Collateral, Leaving Deposit Users Unable to Redeem — (`contracts/L2/RsETHTokenWrapper.sol`)

### Summary

`mint()` creates wrsETH with no corresponding collateral in the contract. Because `_withdraw()` draws from a single shared token balance with no per-path accounting, any bridge-minted wrsETH holder can immediately redeem against collateral deposited by `deposit()`-path users, leaving those users unable to withdraw.

### Finding Description

The contract has two distinct paths for issuing wrsETH:

**Deposit path** — `_deposit()` pulls `_amount` of `_asset` from the caller into the contract, then mints an equal amount of wrsETH. Collateral is present 1:1. [1](#0-0) 

**Bridge/mint path** — `mint()` calls `_mint()` directly with no collateral transfer whatsoever. [2](#0-1) 

The intended design is that the `BRIDGER_ROLE` later calls `depositBridgerAssets()` to top up the contract's balance and back the bridge-minted supply. However, there is no enforcement of ordering or atomicity between `mint()` and `depositBridgerAssets()`. [3](#0-2) 

`_withdraw()` has a single guard — `allowedTokens[_asset]` — and then unconditionally burns wrsETH and transfers `_amount` of `_asset` from the contract's balance. There is no check that the caller's wrsETH was issued via the deposit path, nor any per-path reserve accounting. [4](#0-3) 

### Impact Explanation

Concrete four-step scenario:

1. userA calls `deposit(tokenA, 100e18)` → contract receives 100e18 tokenA, userA receives 100e18 wrsETH. `totalSupply = 100e18`, `balance(tokenA) = 100e18`.
2. MINTER_ROLE (bridge) calls `mint(userB, 100e18)` → userB receives 100e18 wrsETH, no tokenA deposited. `totalSupply = 200e18`, `balance(tokenA) = 100e18`.
3. userB calls `withdraw(tokenA, 100e18)` → burns 100e18 wrsETH, transfers 100e18 tokenA to userB. `totalSupply = 100e18`, `balance(tokenA) = 0`.
4. userA calls `withdraw(tokenA, 100e18)` → `safeTransfer` reverts because the contract holds 0 tokenA.

userA's wrsETH is not destroyed (it still exists as a token), but the contract cannot fulfill the redemption. This matches **Low — contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation

The MINTER_ROLE is held by pool contracts (`RSETHPoolV2`, `RSETHPoolV3ExternalBridge`, etc.) that call `wrsETH.mint()` during normal ETH/token deposits on L2. [5](#0-4) 

This means bridge-minted wrsETH is issued in the ordinary course of protocol operation. Any such recipient can immediately call `withdraw()` before the BRIDGER_ROLE has called `depositBridgerAssets()`. No malicious actor or compromised key is required — the window exists between every bridge mint and the subsequent bridger deposit.

### Recommendation

Track collateral per issuance path. One approach: maintain a `depositPathReserve` mapping per asset that is incremented in `_deposit()` and decremented in `_withdraw()`, and enforce in `_withdraw()` that the contract's per-asset reserve is sufficient. Alternatively, require that `depositBridgerAssets()` is called atomically (same transaction) with `mint()`, or restrict `withdraw()` so that it can only draw against collateral that was deposited via `_deposit()` rather than the shared balance.

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/L2/RsETHTokenWrapper.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {
    constructor() ERC20("AltRsETH", "altRsETH") {
        _mint(msg.sender, 1_000e18);
    }
}

contract DrainTest is Test {
    RsETHTokenWrapper wrapper;
    MockToken tokenA;
    address admin   = address(0xA);
    address bridger = address(0xB);
    address userA   = address(0xC);
    address userB   = address(0xD);
    address minter  = address(0xE);

    function setUp() public {
        tokenA  = new MockToken();
        wrapper = new RsETHTokenWrapper();
        wrapper.initialize(admin, bridger, address(tokenA));

        vm.prank(admin);
        wrapper.grantRole(wrapper.MINTER_ROLE(), minter);

        tokenA.transfer(userA, 100e18);
    }

    function test_bridgeMintDrainsDepositCollateral() public {
        // Step 1: userA deposits 100e18 tokenA
        vm.startPrank(userA);
        tokenA.approve(address(wrapper), 100e18);
        wrapper.deposit(address(tokenA), 100e18);
        vm.stopPrank();

        // Step 2: bridge mints 100e18 wrsETH to userB (no collateral)
        vm.prank(minter);
        wrapper.mint(userB, 100e18);

        // Step 3: userB withdraws, draining all tokenA
        vm.prank(userB);
        wrapper.withdraw(address(tokenA), 100e18);

        assertEq(tokenA.balanceOf(address(wrapper)), 0);

        // Step 4: userA cannot redeem — reverts
        vm.prank(userA);
        vm.expectRevert();
        wrapper.withdraw(address(tokenA), 100e18);
    }
}
```

### Citations

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

**File:** contracts/L2/RsETHTokenWrapper.sol (L162-170)
```text
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, msg.sender, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L190-192)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L298-299)
```text
        wrsETH.mint(msg.sender, rsETHAmount);

```
