# [H] ArrakisMetaVault::setModule Malicious execu-

## Summary
Severity: High
Contest weight: 0.3624
Dataset id: 22826
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious executor, after a new module is whitelisted by an admin, can drain the vault by calling ArrakisStandardManager.setModule() with a malicious payloads_.
The setModule() function of the ArrakisStandardManager contract allows an executor to set a new module for a vault: ArrakisStandardManager.sol#L438.
It calls ValantisModule.withdraw(), to withdraw the funds from the pool and transfer to the new module: ValantisHOTModule.sol#L235.
Once the vault's funds are in the new module, the first malicious payloads_ is executed and calls ValantisModule::initializePosition to deposit the liquidity back into the pool: ValantisHOTModule.sol#L148.
Lastly, the second payloads_ of the malicious executor gets executed and calls ValantisModulePublic::withdraw which calls ValantisModule::withdraw on the new module and withdraws all funds to an arbitrary address: ValantisHOTModule.sol#L203.
Theft of all funds in the vault.
Scenario
1. Owner whitelists a legitimate new module with ArrakisMetaVault::whitelistModules.
2. Malicious public vault executor calls ArrakisStandardManager::setModule with a malicious payloads_.
1. It calls ArrakisMetaVault::setModule.
2. It calls ValantisModulePublic::withdraw which calls _module.withdraw(module_, BASE) to withdraw all vault's funds from old to new module.
3. Malicious executor has provided two payloads
1. The first one calls ValantisModule::initializePosition to deposit liquidity into the new pool.
2. Then the second malicious payloads_ is executed and contains a call to ValantisModule::withdraw with attacker as the receiver direct theft of funds, the executor can also call withdrawManagerBalance which would transfer all the balance of the module to the manager. Or also not call any function at all (payloads is an empty array), and leave the balances in the module.

## Recommendation
Check that the reserves in the new pool are correct after setting the new module, similarly to what is currently done at the end of rrakis/blob/d7946ee784ca8df3246d723e8b92529447e23bb7/arrakis-modular/src/ArrakisStandardManager.sol#L391-L414
