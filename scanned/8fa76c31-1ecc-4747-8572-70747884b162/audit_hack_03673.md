# [M] removePlugin() should check, that all yield are claimed

## Summary
Severity: Medium
Reporter: Chandr
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429
Type: audit-issue

## Details
# removePlugin() should check, that all yield are claimed

## Summary

[removePlugin() ](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429) should check, that all yield are claimed from plugin before removing it from plugin list. Otherwise, the message that the reward has been credited to the account has already been emitted but is not available to the user.

## Vulnerability Detail

Set up: Add plugin contract to module conract, stake some tel from user account. 
1) [add plugin](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L409-L417)
2) [increase rewards of account](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/SimplePlugin.sol#L120-L142)
3) [remove plugin](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429)

Expected behaivor:
User can withdraw both stake and yield

Real behaivor:
User can withdraw  only stake

## Impact

temporary unavailability of yield

## Code Snippet

```solidity
/// @notice Removes a plugin
    function removePlugin(uint256 index) external onlyRole(PLUGIN_EDITOR_ROLE) {
        address plugin = plugins[index];

        pluginsMapping[plugin] = false;
        plugins[index] = plugins[nPlugins - 1];
        plugins.pop();
        nPlugins--;

        emit PluginRemoved(plugin, nPlugins);
    }
```

## Tool used

Manual Review

## Recommendation

Add a check that all yields are received by the user before removing the plugin
