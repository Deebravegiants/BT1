# [M] Uncompilable DeployUsdxlHyperTestnet script

## Summary
Severity: Medium
Contest weight: 0.3906
Dataset id: 8991
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DeployUsdxlHyperTestnet script attempts to use usdxlConfig for deployment configuration but fails to declare it as a state variable. This causes compilation failures and renders the deployment script unusable.
//File: script/DeployUsdxlHyperTestnet.sol
```solidity
function _deploy() internal {
    vm.setEnv('FOUNDRY_ROOT_CHAINID', vm.toString(block.chainid));
    instanceId = 'hypurrfi-testnet';
    config = DeployUsdxlFileUtils.readInput(instanceId);
    @> usdxlConfig = DeployUsdxlFileUtils.readUsdxlInput
    //(instanceId); // @audit usdxlConfig not declared
--- SNIPPED ---
    _deployUsdxl(usdxlConfig.readAddress
    //('.usdxlAdmin'), deployRegistry); // Fails: usdxlConfig not declared
```

## Recommendation
Declare the usdxlConfig state variable in the DeployUsdxlHyperTestnet.
