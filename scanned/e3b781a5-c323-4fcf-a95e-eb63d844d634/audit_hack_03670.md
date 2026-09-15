# [M] addPlugin() shold check, that added contract is plugin

## Summary
Severity: Medium
Reporter: Chandr
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417
Type: audit-issue

## Details
# addPlugin() shold check, that added contract is plugin

## Summary

If you add an address that is not a plugin with [addPlugin()](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417), then the user will not be able to use the [stake()](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L157-L163) function, even if a valid contract with the plugin has been added before

## Vulnerability Detail

1) [add](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417) valid plugin(simple plugin) to module contract
2) [add](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417) not valid plugin(address(0x42)) to module contract
3) Try to [stake](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L157-L166)

## Impact

Expected behaivor:
User can stake to valid plugin, even though there is an invalid plugin in the [list of plugins](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L34)

Real behaivor:
Transer reverted with: "EvmError: Revert"

## Impact

User cannot deposit funds to stake

## Code Snippet

```solidity
function addPlugin(address plugin) external onlyRole(PLUGIN_EDITOR_ROLE) {
        require(!pluginsMapping[plugin], "StakingModule::addPlugin: Cannot add an existing plugin");

        plugins.push(plugin);
        pluginsMapping[plugin] = true;
        nPlugins++;

        emit PluginAdded(plugin, nPlugins);
    }

```

## Tool used

Manual Review

## Recommendation

Add a check when adding a plugin that the plugin is a valid contract
