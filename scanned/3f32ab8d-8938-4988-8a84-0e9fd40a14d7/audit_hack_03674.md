# [M] Deletion of plugin by administrator will result in loss of user reward

## Summary
Severity: Medium
Reporter: 8olidity
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429
Type: audit-issue

## Details
# Deletion of plugin by administrator will result in loss of user reward

## Summary
Deletion of plugin by administrator will result in loss of user reward
## Vulnerability Detail
In a `stakingmodule.sol` contract, an administrator can delete an plugin address.

```solidity
    function removePlugin(uint256 index) external onlyRole(PLUGIN_EDITOR_ROLE) {
        address plugin = plugins[index];

        pluginsMapping[plugin] = false;
        plugins[index] = plugins[nPlugins - 1];
        plugins.pop();
        nPlugins--;

        emit PluginRemoved(plugin, nPlugins);
    }
```

But there is no check for deletion. The user's reward in this plugin is also not sent to the user. But delete it directly. Cause the loss of the user's reward

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

## Impact
Deletion of plugin by administrator will result in loss of user reward
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L262-L281
## Tool used

Manual Review

## Recommendation
Distribute the user's reward to the user during removePlugin
