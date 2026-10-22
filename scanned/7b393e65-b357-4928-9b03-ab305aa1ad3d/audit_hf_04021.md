# [M] getReservesByCategory() when useSubmodules

## Summary
Severity: Medium
Contest weight: 0.7891
Dataset id: 20436
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In getReservesByCategory() lack of check data.submoduleReservesSelector!="0x00000000" when call submodule.staticcall(abi.encodeWithSelector(data.submoduleReservesSelector)); will revert when _addCategory() if useSubmodules==true, submoduleMetricSelector must not be empty and submoduleReservesSelector can be empty (bytes4(0)) like "protocol-owned-treasury"
```solidity
_addCategory(toCategory("protocol-owned-treasury"), true, 0xb600c5e2, 0x00000000); // getProtocolOwnedTreasuryOhm()
```

But when call getReservesByCategory(), don't check submoduleReservesSelector!=bytes4(0) and directly call submoduleReservesSelector
```solidity
function getReservesByCategory(
    Category category_
) external view override returns (Reserves[] memory) {
    ...
    // If category requires data from submodules, count all submodules and their sources.
    len = (data.useSubmodules) ? submodules.length : 0;
    ...
    for (uint256 i; i < len; ) {
        address submodule = address(_getSubmoduleIfInstalled(submodules[i]));
        (bool success, bytes memory returnData) = submodule.staticcall(
            abi.encodeWithSelector(data.submoduleReservesSelector)
        );
```

This way, when call like getReservesByCategory(toCategory("protocol-owned-treasury")) will revert, some category can't get Reserves.

## Proof of Concept
add to SUPPLY.v1.t.sol
```solidity
function test_getReservesByCategory_includesSubmodules_treasury() public {
    _setUpSubmodules();
    // Add OHM/gOHM in the treasury (which will not be included)
    ohm.mint(address(treasuryAddress), 100e9);
    gohm.mint(address(treasuryAddress), 1e18); // 1 gOHM
    // Categories already defined
    uint256 expectedBptDai = BPT_BALANCE.mulDiv(
        BALANCER_POOL_DAI_BALANCE,
        BALANCER_POOL_TOTAL_SUPPLY
    );
    uint256 expectedBptOhm = BPT_BALANCE.mulDiv(
        BALANCER_POOL_OHM_BALANCE,
        BALANCER_POOL_TOTAL_SUPPLY
    );
    // Check reserves
    SPPLYv1.Reserves[] memory reserves = moduleSupply.getReservesByCategory(
        toCategory("protocol-owned-treasury")
    );
}
```
forge test -vv --match-test test_getReservesByCategory_includesSubmodules_treasury

Running 1 test for src/test/modules/SPPLY/SPPLY.v1.t.sol:SupplyTest
[FAIL. Reason: SPPLY_SubmoduleFailed(0xeb502B1d35e975321B21cCE0E8890d20a7Eb289d, 0x0000000000000000000000000000000000000000000000000000000000000000)] test_getReservesByCategory_includesSubmodules_treasury() (gas: 4774197

## Recommendation
```solidity
function getReservesByCategory(
    Category category_
) external view override returns (Reserves[] memory) {
    ...
    CategoryData memory data = categoryData[category_];
    uint256 categorySubmodSources;
    // If category requires data from submodules, count all submodules and their sources.
    len = (data.useSubmodules && data.submoduleReservesSelector != bytes4(0)) ? submodules.length : 0;
```
