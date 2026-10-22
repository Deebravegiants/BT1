# [M] createMarket and createBorrowATokenV1_5 always fail due to owner() being set to address(0) after v1.7 upgrade

## Summary
Severity: Medium
Reporter: pep7siup, also found by serial-coder, mt030d, Josh4324, kalogerone, gimoquoi, gimoquoi, 0xEkkoo, Kasheeda, korok, rokino
Contest weight: 0.7507
Dataset id: 4904
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The upgrade process for SizeFactory v1.7 includes renouncing ownership, effectively setting owner() to address(0). However, both createMarket and createBorrowATokenV1_5 rely on owner() when calling initialization functions, leading to reverts when owner() is checked.
• Found in src/factory/SizeFactory.sol at SizeFactory.sol#L123:
```solidity
function createMarket(
// ...
    market = MarketFactoryLibrary.createMarket(
        sizeImplementation, owner(), feeConfigParams, riskConfigParams, oracleParams, dataParams
    );
// ...
}
```
// Initialize.sol: createMarket -> Size:initialize -> validateOwner reverts if owner is null address
```solidity
function validateOwner(address owner) internal pure {
    if (owner == address(0)) {
        revert Errors.NULL_ADDRESS();
    }
}
```
The function MarketFactoryLibrary.createMarket() attempts to pass owner() but fails due to NULL_ADDRESS.
• Found in src/factory/SizeFactory.sol at SizeFactory.sol#L183.
```solidity
function createBorrowATokenV1_5(IPool variablePool, IERC20Metadata underlyingBorrowToken)
// ...
    borrowATokenV1_5 =
        NonTransferrableScaledTokenV1_5FactoryLibrary.createNonTransferrableScaledTokenV1_5(
            nonTransferrableScaledTokenV1_5Implementation, owner(), variablePool, underlyingBorrowToken
        );
// ...
}
```
In createBorrowATokenV1_5, the function createNonTransferrableScaledTokenV1_5() also passes owner(), leading to an OwnableInvalidOwner error. This breaks the ability to create new markets or borrowing tokens, making key protocol functions unusable post-upgrade.

Impact Explanation:
The issue completely prevents the creation of new markets and borrow tokens, significantly impairing the protocol’s functionality, making this a high-impact issue.

## Proof of Concept
Apply and run with:
`FOUNDRY_PROFILE=fork FOUNDRY_INVARIANT_RUNS=0 FOUNDRY_INVARIANT_DEPTH=0 forge test --mc ForkReinitializeV1_7Test --mt testFork_ForkReinitializeV1_7_reinitialize --ffi -vvvv`
```diff
diff --git a/test/fork/v1.7/ForkReinitializeV1_7.t.sol b/test/fork/v1.7/ForkReinitializeV1_7.t.sol
index 196ae35..ccf5b8f 100644
--- a/test/fork/v1.7/ForkReinitializeV1_7.t.sol
+++ b/test/fork/v1.7/ForkReinitializeV1_7.t.sol
@@ -30,6 +30,9 @@ contract ForkReinitializeV1_7Test is ForkTest, GetV1_7ReinitializeDataScript, Ne
    address owner;
}
+
error NULL_ADDRESS();
+
error OwnableInvalidOwner(address owner);
+
function _getV1_7ReinitializeAddresses(string memory network, uint256 blockNumber)
private
returns (Vars memory vars)
@@ -87,11 +90,20 @@ contract ForkReinitializeV1_7Test is ForkTest, GetV1_7ReinitializeDataScript, Ne
    address(vars.sizeFactory).call(abi.encodeWithSelector(IAccessControl.hasRole.selector, vars.owner, 0x00));
    assertTrue(success, "should be able to call hasRole");
    assertTrue(OwnableUpgradeable(address(vars.sizeFactory)).owner() == address(0), "owner should be set to zero");
+
+
    vm.startPrank(vars.owner);
+
    vm.expectRevert(abi.encodeWithSelector(NULL_ADDRESS.selector));
+
    vars.sizeFactory.createMarket(f, r, o, d);
+
+
+
    vm.expectRevert(abi.encodeWithSelector(OwnableInvalidOwner.selector, address(0)));
+
    vars.sizeFactory.createBorrowATokenV1_5(variablePool, usdc);
+
    vm.stopPrank();
}
function testFork_ForkReinitializeV1_7_reinitialize() public {
    // 2025-02-21T12:00Z
    // _testFork_ForkReinitializeV1_7_reinitialize("mainnet", 21894565);
    _testFork_ForkReinitializeV1_7_reinitialize("base-production", 26674900);
}
```

## Recommendation
Modify createMarket and createBorrowATokenV1_5 to accept owner as an explicit parameter instead of relying on owner(), ensuring that a valid owner address is always provided:
```solidity
function createMarket(address _owner, ...) external {
    market = MarketFactoryLibrary.createMarket(
        sizeImplementation, _owner, feeConfigParams, riskConfigParams, oracleParams, dataParams
    );
}
function createBorrowATokenV1_5(address _owner, IPool variablePool, IERC20Metadata underlyingBorrowToken) external {
    borrowATokenV1_5 = NonTransferrableScaledTokenV1_5FactoryLibrary.createNonTransferrableScaledTokenV1_5(
        nonTransferrableScaledTokenV1_5Implementation, _owner, variablePool, underlyingBorrowToken
    );
}
```
