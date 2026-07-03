### Title
Stale Off-Chain Cap Read Allows Temporary Under-Collateralization of Minted agETH — (`contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

`depositBridgerAssets` only enforces an upper bound on the deposit amount (`_amount ≤ cap`), but does not enforce that the bridger deposits the **full current cap**. Because `mint` can legitimately increase `totalSupply` between the bridger's off-chain read of `maxAmountToDepositBridgerAsset` and the on-chain execution of `depositBridgerAssets`, the bridger deposits against a stale cap, leaving the newly minted agETH temporarily unbacked and un-withdrawable.

---

### Finding Description

`maxAmountToDepositBridgerAsset` computes the uncollateralized gap as:

```
cap = totalSupply() - balanceOfAssetInWrapper
``` [1](#0-0) 

`depositBridgerAssets` re-evaluates this at call time and only reverts if `_amount > cap`:

```solidity
if (maxAmountToDepositBridgerAsset(_asset) < _amount) revert CannotDeposit();
``` [2](#0-1) 

`mint` (callable by any `MINTER_ROLE` holder — the bridge contract in normal operation) increases `totalSupply` without adding any backing:

```solidity
function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
    _mint(_to, _amount);
}
``` [3](#0-2) 

**Race sequence (no malicious intent required):**

| Step | Action | `totalSupply` | `balance` | `cap` |
|------|--------|--------------|-----------|-------|
| 0 | Initial state | S | B | C = S−B |
| 1 | Bridger reads cap off-chain | S | B | C |
| 2 | Bridge mints D agETH (normal bridge operation) | S+D | B | C+D |
| 3 | Bridger calls `depositBridgerAssets(asset, C)` | S+D | B | C+D |
| 4 | Check: `C+D >= C` → passes; deposits C | S+D | B+C | D |

After step 4, `D` agETH exist with zero backing. Any holder of those `D` agETH who calls `withdraw` will hit the `safeTransfer` in `_withdraw`:

```solidity
ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
``` [4](#0-3) 

This reverts because the contract holds only `B+C` altAgETH against `S+D` agETH supply. The `D` agETH holders cannot withdraw until the bridger makes a second `depositBridgerAssets` call covering the remaining `D`.

---

### Impact Explanation

Holders of the `D` freshly-minted agETH (received via the bridge) temporarily cannot redeem their tokens for altAgETH. The contract fails to deliver the promised 1:1 redemption. No value is permanently lost — the bridger's next deposit cycle restores full collateralization — but the window of non-redeemability is real and observable.

**Scope: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

This requires no malicious actor. The MINTER_ROLE is the bridge contract performing its normal function (minting agETH for users bridging from L1). The BRIDGER_ROLE is performing its normal function (depositing backing assets). The race is an inherent consequence of the two-step off-chain-read / on-chain-deposit design. On any active L2 deployment with regular bridge traffic, concurrent mints between the bridger's read and deposit are routine.

---

### Recommendation

Replace the caller-supplied `_amount` with the live cap computed atomically inside `depositBridgerAssets`, so the bridger always deposits exactly the current uncollateralized gap in a single atomic operation:

```solidity
function depositBridgerAssets(address _asset) external onlyRole(BRIDGER_ROLE) {
    uint256 amount = maxAmountToDepositBridgerAsset(_asset);
    if (amount == 0) revert CannotDeposit();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), amount);
    emit BridgerDeposited(_asset, amount);
}
```

This eliminates the stale-read window entirely: the cap is read and consumed atomically within the same transaction.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "forge-std/Test.sol";
import "../contracts/agETH/AGETHTokenWrapper.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockAltAgETH is ERC20 {
    constructor() ERC20("altAgETH", "altAgETH") {}
    function mint(address to, uint256 amount) external { _mint(to, amount); }
}

contract AGETHRaceTest is Test {
    AGETHTokenWrapper wrapper;
    MockAltAgETH altAgETH;

    address admin    = address(1);
    address manager  = address(2);   // BRIDGER_ROLE
    address minter   = address(3);   // MINTER_ROLE
    address user     = address(4);   // receives minted agETH
    address bridgee  = address(5);   // receives bridged agETH

    function setUp() public {
        altAgETH = new MockAltAgETH();
        wrapper  = new AGETHTokenWrapper();
        wrapper.initialize(admin, manager, address(altAgETH));

        // Grant MINTER_ROLE to minter
        vm.prank(admin);
        wrapper.grantRole(wrapper.MINTER_ROLE(), minter);

        // Seed bridger with altAgETH
        altAgETH.mint(manager, 200e18);
        vm.prank(manager);
        altAgETH.approve(address(wrapper), type(uint256).max);
    }

    function test_staleCapRaceCondition() public {
        // Step 1: Bridger reads cap = 100e18 (off-chain)
        // Simulate: wrapper has 100e18 agETH minted, 0 backing
        vm.prank(minter);
        wrapper.mint(user, 100e18);

        uint256 capBeforeMint = wrapper.maxAmountToDepositBridgerAsset(address(altAgETH));
        assertEq(capBeforeMint, 100e18, "cap should be 100e18");

        // Step 2: Bridge mints 50e18 agETH for a new bridging user (normal operation)
        vm.prank(minter);
        wrapper.mint(bridgee, 50e18);

        // Step 3: Bridger deposits only the stale cap (100e18), not the new cap (150e18)
        vm.prank(manager);
        wrapper.depositBridgerAssets(address(altAgETH), capBeforeMint); // passes: 150e18 >= 100e18

        // Step 4: Assert 50e18 agETH held by bridgee are unbacked
        uint256 remainingCap = wrapper.maxAmountToDepositBridgerAsset(address(altAgETH));
        assertEq(remainingCap, 50e18, "50e18 agETH are unbacked");

        // Step 5: bridgee cannot withdraw — safeTransfer reverts (insufficient altAgETH balance)
        vm.prank(bridgee);
        vm.expectRevert(); // ERC20: transfer amount exceeds balance
        wrapper.withdraw(address(altAgETH), 50e18);
    }
}
```

The test demonstrates that after the bridger deposits the stale cap, `bridgee`'s 50e18 agETH are unredeemable until the bridger makes a second `depositBridgerAssets` call.

### Citations

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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L114-117)
```text
        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L143-151)
```text
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L165-167)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```
