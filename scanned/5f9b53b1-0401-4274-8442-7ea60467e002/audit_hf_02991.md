# [H] `MIMOEmptyVault.sol executeOperation`

## Summary
Severity: High
Contest weight: 0.9134
Dataset id: 16669
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`MIMOEmptyVault.sol executeAction()` is supposed to pay off the debt and return the leftover assets to the owner of the Vault. But in fact the emptyVault contract, after executing the executionOperation(), only pays back the flash loan, and does not transfer the leftover assets to the owner, and locked in the emptyVault contract.

## Proof of Concept
```solidity
function executeOperation(
    address[] calldata assets,
    uint256[] calldata amounts,
    uint256[] calldata premiums,
    address initiator,
    bytes calldata params
) external override returns (bool) {

    ....
    ....

    require(flashloanRepayAmount <= vaultCollateral.balanceOf(address(this)), Errors.CANNOT_REPAY_FLASHLOAN);

    vaultCollateral.safeIncreaseAllowance(address(lendingPool), flashloanRepayAmount);

    //****Paid off the flash loan but did not transfer the remaining balance back to mimoProxy or owner ***//

    return true;
}
```

Add logs to test case

test/02_integration/MIMOEmtpyVault.test.ts

```solidity
it("should be able to empty vault with 1inch", async () => {
    ...
    ...
    ...
    console.log("before emptyVault balance:--->", (await wmatic.balanceOf(emptyVault.address)) + "");
    const tx = await mimoProxy.execute(emptyVault.address, MIMOProxyData);
    const receipt = await tx.wait(1);
    console.log("after emptyVault balance: --->", (await wmatic.balanceOf(emptyVault.address)) + "");
```

print:

    before emptyVault balance:---> 0
    after emptyVault balance: ---> 44383268870065355782

## Recommendation
```solidity
function executeOperation(
    address[] calldata assets,
    uint256[] calldata amounts,
    uint256[] calldata premiums,
    address initiator,
    bytes calldata params
) external override returns (bool) {

    ....
    ....

    require(flashloanRepayAmount <= vaultCollateral.balanceOf(address(this)), Errors.CANNOT_REPAY_FLASHLOAN);

    vaultCollateral.safeIncreaseAllowance(address(lendingPool), flashloanRepayAmount);

    //****transfer the remaining balance back to mimoProxy or owner ***//
    vaultCollateral.safeTransfer(address(mimoProxy), vaultCollateral.balanceOf(address(this)) - flashloanRepayAmount);

    return true;
}
```

We confirm this is a vulnerability and intend to fix this - only the amount needed to repay the flashloan should be transferred from the `MimoProxy` to the `MIMOEmptyVault` action contract.

**horsefacts (warden) reviewed mitigation:**

**Status:** ✅ Resolved

**Finding:** Wardens identified that `MIMOEmptyVault` transferred in a vault’s full collateral balance when repaying vault rebalance flash loans, but did not return excess collateral to the vault owner when the flash loan repayment amount was less than the vault’s collateral balance. Instead, the excess amount would be locked in the action contract.

**What changed:** The Mimo team updated `MIMOEmptyVault#emptyVaultOperation` to transfer collateral exactly equal to the [flashloan repayment amount](https://github.com/mimo-capital/2022-08-mimo/blob/5186ef4be23f9dda81c8474096edb1f0594d70c3/contracts/actions/MIMOEmptyVault.sol#L142), rather than the full vault balance. This behavior is demonstrated by an [integration test](https://github.com/mimo-capital/2022-08-mimo/blob/5186ef4be23f9dda81c8474096edb1f0594d70c3/test/02_integration/MIMOEmtpyVault.test.ts#L297).

**Why it works:** Since excess collateral is never transferred to `MIMOEmptyVault`, it can no longer be locked in the contract.
