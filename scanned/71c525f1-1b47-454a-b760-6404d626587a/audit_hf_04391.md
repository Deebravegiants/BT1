# [M] `executeYieldBorrowERC20` calculates totalSupply using the wrong index

## Summary
Severity: Medium
Contest weight: 0.1908
Dataset id: 21659
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `executeYieldBorrowERC20()`, we will check whether `stakerAddr` exceeds `yieldCap`.

      function executeYieldBorrowERC20(InputTypes.ExecuteYieldBorrowERC20Params memory params) internal {
    ...
        ValidateLogic.validateYieldBorrowERC20(params, poolData, assetData, groupData);

        vars.totalSupply = VaultLogic.erc20GetTotalCrossSupply(assetData, groupData.borrowIndex);

        // check asset level yield cap limit
        vars.totalBorrow = VaultLogic.erc20GetTotalCrossBorrowInGroup(groupData, groupData.borrowIndex);
        require(
          (vars.totalBorrow + params.amount) <= vars.totalSupply.percentMul(assetData.yieldCap),
          Errors.YIELD_EXCEED_ASSET_CAP_LIMIT
        );

        // check staker level yield cap limit
        vars.stakerBorrow = VaultLogic.erc20GetUserCrossBorrowInGroup(groupData, vars.stakerAddr, groupData.borrowIndex);
        require(
          (vars.stakerBorrow + params.amount) <= vars.totalSupply.percentMul(ymData.yieldCap),
          Errors.YIELD_EXCEED_STAKER_CAP_LIMIT
        );

The code above, calculating `totalSupply` using `totalSupply = totalScaledCrossSupply * groupData.borrowIndex` to calculate `supply` is wrong. The correct way to calculate `supply` is to use: `assetData.supplyIndex`.

## Recommendation
function executeYieldBorrowERC20(InputTypes.ExecuteYieldBorrowERC20Params memory params) internal {
    ...
        ValidateLogic.validateYieldBorrowERC20(params, poolData, assetData, groupData);

        vars.totalSupply = VaultLogic.erc20GetTotalCrossSupply(assetData, assetData.supplyIndex);

        // check asset level yield cap limit
        vars.totalBorrow = VaultLogic.erc20GetTotalCrossBorrowInGroup(groupData, groupData.borrowIndex);
