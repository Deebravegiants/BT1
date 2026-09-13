# [M] Plugin removal can freeze user funds

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L419-L429
Type: audit-issue

## Details
# Plugin removal can freeze user funds

## Summary

There are no checks that plugin being removed doesn't hold meaningful funds claimable. As users don't have direct access to plugins the removal means losing the access to the funds within.

## Vulnerability Detail

Users access plugins via StakingModule, which tracks the list of active ones. If a plugin holds funds, but is removed from StakingModule's list, the users will lose the access to these funds.

## Impact

User funds are frozen within the plugin removed with no means to access them until the plugin be added back.

This can be a permanent freeze, but setting severity to be medium due to prerequisites.

## Code Snippet

StakingModule#removePlugin() doesn't check if there are funds left with it:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L419-L429

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

If a plugin with positive totalClaimable() is removed this way, the corresponding funds of the users become inaccessible for them as plugins can interact only with StakingModule.

Citing claiming functions as an example:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L262-L281

```solidity
    function _claim(address account, address to, bytes calldata auxData) private returns (uint256) {
        // balance of `to` before claiming
        uint256 balBefore = IERC20Upgradeable(tel).balanceOf(to);

        // call claim on all plugins and count the total amount claimed
        uint256 total;
        for (uint256 i = 0; i < nPlugins; i++) {
            total += IPlugin(plugins[i]).claim(account, to, auxData);
        }

        // make sure `total` actually matches how much we've claimed
        require(IERC20Upgradeable(tel).balanceOf(to) - balBefore == total, "one or more plugins did not send appropriate token amount");

        // only emit Claimed if anything was actually claimed
        if (total > 0) {
            emit Claimed(account, total);
        }

        return total;
    }
```

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L234-L252

```solidity
    function _claimFromIndividualPlugin(address account, address to, uint256 pluginIndex, bytes calldata auxData) private returns (uint256) {
        require(pluginIndex < nPlugins, "StakingModule::_claimFromIndividualPlugin: Provided pluginIndex is out of bounds");
        
        // balance of `to` before claiming
        uint256 balBefore = IERC20Upgradeable(tel).balanceOf(to);

        // xClaimed = "amount of TEL claimed from the plugin"
        uint256 xClaimed = IPlugin(plugins[pluginIndex]).claim(account, to, auxData);

        // we want to make sure the plugin did not return the wrong amount
        require(IERC20Upgradeable(tel).balanceOf(to) - balBefore == xClaimed, "The plugin did not send appropriate token amount");

        // only emit Claimed if anything was actually claimed
        if (xClaimed > 0) {
            emit Claimed(account, xClaimed);
        }

        return xClaimed;
    }
```
## Tool used

Manual Review

## Recommendation

Consider adding the control for plugin to be empty (say up to some threshold to avoid dust amounts interfering with the workflow), for example:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L419-L429

```solidity
    /// @notice Removes a plugin
    function removePlugin(uint256 index) external onlyRole(PLUGIN_EDITOR_ROLE) {
        address plugin = plugins[index];
+       require(IPlugin(plugin).totalClaimable() < DUST_THRESHOLD, "removePlugin: plugin not empty");
        pluginsMapping[plugin] = false;
        plugins[index] = plugins[nPlugins - 1];
        plugins.pop();
        nPlugins--;

        emit PluginRemoved(plugin, nPlugins);
    }
```
